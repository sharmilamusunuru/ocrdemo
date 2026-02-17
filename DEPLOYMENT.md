# Deployment Guide

This guide provides step-by-step instructions for deploying the OCR Demo application to Azure.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Infrastructure Deployment](#infrastructure-deployment)
3. [Application Deployment](#application-deployment)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- **Azure CLI** (v2.50+): [Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Terraform** (v1.0+): [Install Guide](https://www.terraform.io/downloads)
- **Python** (v3.11+): [Download](https://www.python.org/downloads/)
- **Git**: [Download](https://git-scm.com/downloads)

### Azure Requirements
- Azure subscription with appropriate permissions
- Access to create the following resources:
  - Resource Groups
  - App Services
  - Azure Functions
  - Storage Accounts
  - Cognitive Services
  - Azure OpenAI

### Check Azure Quotas
```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "<your-subscription-id>"

# Check regional availability for Azure OpenAI
az cognitiveservices account list-skus \
  --kind OpenAI \
  --location eastus
```

## Infrastructure Deployment

### Step 1: Clone Repository
```bash
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo
```

### Step 2: Configure Terraform Variables

Edit `terraform/terraform.tfvars` (create if it doesn't exist):
```hcl
resource_group_name      = "rg-ocr-demo-prod"
location                 = "eastus"
storage_account_name     = "stocrdemo12345"  # Must be globally unique
document_intelligence_name = "di-ocr-demo"
openai_name              = "oai-ocr-demo"
app_service_plan_name    = "asp-ocr-demo"
app_service_name         = "app-sap-simulator-demo"  # Must be globally unique

tags = {
  Environment = "Production"
  Project     = "OCR-Demo"
  Owner       = "YourName"
}
```

### Step 3: Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan -out=tfplan

# Apply infrastructure changes
terraform apply tfplan
```

This will create:
- Resource Group
- Storage Account with Blob Container
- Azure Document Intelligence resource
- Azure OpenAI resource
- App Service Plan
- App Service (for SAP Simulator)

**Note**: This takes about 5-10 minutes.

### Step 4: Save Terraform Outputs

```bash
# Save all outputs to a file
terraform output -json > ../outputs.json

# Display specific outputs
terraform output storage_connection_string
terraform output document_intelligence_endpoint
terraform output openai_endpoint
terraform output web_app_url
```

## Application Deployment

### Option A: Automated Deployment (Recommended)

```bash
cd ..
chmod +x deploy.sh
./deploy.sh
```

This script will:
1. Deploy infrastructure with Terraform
2. Create .env file with Azure credentials
3. Deploy SAP Simulator to App Service
4. Deploy Validation Service to Azure Functions

### Option B: Manual Deployment

#### Deploy SAP Simulator to App Service

```bash
cd sap_simulator

# Create requirements.txt for the service
cat > requirements.txt << EOF
Flask==3.0.0
Werkzeug==3.0.1
azure-storage-blob==12.19.0
requests==2.31.0
python-dotenv==1.0.0
EOF

# Deploy to App Service
az webapp up \
  --name <your-app-service-name> \
  --resource-group <your-resource-group> \
  --runtime "PYTHON:3.11" \
  --sku B1
```

#### Deploy Validation Service to Azure Functions

**Option 1: As an App Service (Simpler)**
```bash
cd ../validation_service

# Create requirements.txt
cat > requirements.txt << EOF
Flask==3.0.0
Werkzeug==3.0.1
azure-storage-blob==12.19.0
azure-ai-formrecognizer==3.3.2
azure-core==1.29.6
openai==1.12.0
python-dotenv==1.0.0
EOF

# Deploy as separate App Service
az webapp create \
  --name <validation-service-name> \
  --resource-group <your-resource-group> \
  --plan <your-app-service-plan> \
  --runtime "PYTHON:3.11"

# Deploy code
az webapp up \
  --name <validation-service-name> \
  --resource-group <your-resource-group>
```

**Option 2: As Azure Functions (Production Recommended)**
```bash
cd ../validation_service

# Install Azure Functions Core Tools
# Windows: winget install Microsoft.Azure.Functions.CoreTools
# macOS: brew tap azure/functions && brew install azure-functions-core-tools@4
# Linux: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local

# Initialize Functions project
func init . --python

# Create HTTP triggered function
func new --name ValidateQuantity --template "HTTP trigger"

# Publish to Azure
func azure functionapp publish <your-function-app-name>
```

## Configuration

### Step 1: Configure Azure OpenAI Deployment

The Azure OpenAI resource needs a GPT-4 model deployment:

```bash
# Create GPT-4 deployment
az cognitiveservices account deployment create \
  --name <your-openai-resource-name> \
  --resource-group <your-resource-group> \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

### Step 2: Configure App Service Environment Variables

```bash
# Get values from Terraform outputs
STORAGE_CONNECTION=$(terraform output -raw storage_connection_string)
DOC_INTEL_ENDPOINT=$(terraform output -raw document_intelligence_endpoint)
DOC_INTEL_KEY=$(terraform output -raw document_intelligence_key)
OPENAI_ENDPOINT=$(terraform output -raw openai_endpoint)
OPENAI_KEY=$(terraform output -raw openai_key)

# Set environment variables for SAP Simulator
az webapp config appsettings set \
  --name <sap-simulator-app-name> \
  --resource-group <your-resource-group> \
  --settings \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION" \
    AZURE_STORAGE_CONTAINER_NAME="discharge-documents" \
    VALIDATION_SERVICE_URL="https://<validation-service-name>.azurewebsites.net"

# Set environment variables for Validation Service
az webapp config appsettings set \
  --name <validation-service-name> \
  --resource-group <your-resource-group> \
  --settings \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION" \
    AZURE_STORAGE_CONTAINER_NAME="discharge-documents" \
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="$DOC_INTEL_ENDPOINT" \
    AZURE_DOCUMENT_INTELLIGENCE_KEY="$DOC_INTEL_KEY" \
    AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
    AZURE_OPENAI_KEY="$OPENAI_KEY" \
    AZURE_OPENAI_DEPLOYMENT="gpt-4"
```

### Step 3: Enable CORS (if needed)

```bash
# Enable CORS for Validation Service
az webapp cors add \
  --name <validation-service-name> \
  --resource-group <your-resource-group> \
  --allowed-origins "https://<sap-simulator-app-name>.azurewebsites.net"
```

## Verification

### Step 1: Check Health Endpoints

```bash
# Check SAP Simulator
curl https://<sap-simulator-app-name>.azurewebsites.net/health

# Check Validation Service
curl https://<validation-service-name>.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "SAP Simulator",
  "storage_configured": true,
  "validation_service_reachable": true
}
```

### Step 2: Test End-to-End

1. Generate test documents:
```bash
python create_sample_docs.py
```

2. Open SAP Simulator in browser:
```
https://<sap-simulator-app-name>.azurewebsites.net
```

3. Upload `sample_discharge_document.pdf`
4. Enter quantity: `1234.56`
5. Click "Save"
6. Verify: Should show **"Validation Successful"**

### Step 3: Test API Directly

```bash
# First, upload a file to blob storage
az storage blob upload \
  --account-name <storage-account-name> \
  --container-name discharge-documents \
  --name test.pdf \
  --file sample_discharge_document.pdf

# Then call validation API
curl -X POST \
  https://<validation-service-name>.azurewebsites.net/api/validate \
  -H "X-Discharge-Quantity: 1234.56" \
  -H "Content-Type: application/json" \
  -d '{"blob_name": "test.pdf"}'
```

## Monitoring

### Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app <app-insights-name> \
  --location <location> \
  --resource-group <your-resource-group> \
  --application-type web

# Get Instrumentation Key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app <app-insights-name> \
  --resource-group <your-resource-group> \
  --query instrumentationKey -o tsv)

# Configure App Service to use Application Insights
az webapp config appsettings set \
  --name <sap-simulator-app-name> \
  --resource-group <your-resource-group> \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY"
```

### View Logs

```bash
# Stream logs from SAP Simulator
az webapp log tail \
  --name <sap-simulator-app-name> \
  --resource-group <your-resource-group>

# Stream logs from Validation Service
az webapp log tail \
  --name <validation-service-name> \
  --resource-group <your-resource-group>
```

## Troubleshooting

### Issue: "Storage connection string not found"

**Solution**:
```bash
# Verify storage account exists
az storage account show \
  --name <storage-account-name> \
  --resource-group <your-resource-group>

# Get connection string
az storage account show-connection-string \
  --name <storage-account-name> \
  --resource-group <your-resource-group>
```

### Issue: "Document Intelligence endpoint not responding"

**Solution**:
```bash
# Check if resource is provisioned
az cognitiveservices account show \
  --name <doc-intelligence-name> \
  --resource-group <your-resource-group>

# Verify endpoint and key
az cognitiveservices account show \
  --name <doc-intelligence-name> \
  --resource-group <your-resource-group> \
  --query "properties.endpoint"

az cognitiveservices account keys list \
  --name <doc-intelligence-name> \
  --resource-group <your-resource-group>
```

### Issue: "Azure OpenAI quota exceeded"

**Solution**:
1. Check your quota limits in Azure Portal
2. Request quota increase: Portal > Azure OpenAI > Quotas
3. Or use a different region

### Issue: "App Service deployment failed"

**Solution**:
```bash
# Check deployment logs
az webapp log deployment show \
  --name <app-name> \
  --resource-group <your-resource-group>

# Restart the app
az webapp restart \
  --name <app-name> \
  --resource-group <your-resource-group>
```

## Clean Up

To remove all resources:

```bash
# Using Terraform
cd terraform
terraform destroy

# Or manually
az group delete \
  --name <your-resource-group> \
  --yes --no-wait
```

## Production Checklist

Before going to production:
- [ ] Enable HTTPS only
- [ ] Configure custom domain
- [ ] Set up SSL certificates
- [ ] Enable Application Insights
- [ ] Configure autoscaling
- [ ] Set up backup and disaster recovery
- [ ] Implement API authentication (OAuth 2.0/API keys)
- [ ] Add API Management
- [ ] Configure network security (VNet integration)
- [ ] Set up CI/CD pipelines
- [ ] Enable Azure Key Vault for secrets
- [ ] Configure monitoring and alerts
- [ ] Set up log retention policies
- [ ] Document runbook procedures
- [ ] Perform load testing
- [ ] Create disaster recovery plan

## Support

For issues or questions:
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Review [FLOW_DIAGRAMS.md](FLOW_DIAGRAMS.md) for process flows
- Check Azure service health: https://status.azure.com/
- Azure support: https://azure.microsoft.com/support/
