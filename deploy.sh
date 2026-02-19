#!/bin/bash
# Deployment script for OCR Demo to Azure

set -e

echo "🚀 Starting Azure Deployment for OCR Demo"
echo "=========================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first."
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install it first."
    echo "Visit: https://www.terraform.io/downloads"
    exit 1
fi

# Login to Azure
echo "📝 Logging into Azure..."
az login

# Set subscription (optional - uncomment and set your subscription ID)
# az account set --subscription "your-subscription-id"

# Initialize Terraform
echo "🔧 Initializing Terraform..."
cd terraform
terraform init

# Plan infrastructure
echo "📋 Planning infrastructure deployment..."
terraform plan -out=tfplan

# Confirm deployment
read -p "Do you want to deploy the infrastructure? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled."
    exit 0
fi

# Apply Terraform
echo "🏗️  Deploying infrastructure..."
terraform apply tfplan

# Get outputs
echo "📤 Retrieving deployment outputs..."
STORAGE_CONNECTION=$(terraform output -raw storage_connection_string)
DOC_INTEL_ENDPOINT=$(terraform output -raw document_intelligence_endpoint)
DOC_INTEL_KEY=$(terraform output -raw document_intelligence_key)
OPENAI_ENDPOINT=$(terraform output -raw openai_endpoint)
OPENAI_KEY=$(terraform output -raw openai_key)
WEB_APP_NAME=$(terraform output -raw web_app_name)
CONTAINER_NAME=$(terraform output -raw blob_container_name)

# Get Function App name
FUNCTION_APP_NAME=$(terraform output -raw function_app_name)
FUNCTION_APP_URL=$(terraform output -raw function_app_url)

# Create .env file (for local development only)
echo "📝 Creating .env file..."
cd ..
cat > .env << EOF
AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION
AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=$DOC_INTEL_ENDPOINT
AZURE_DOCUMENT_INTELLIGENCE_KEY=$DOC_INTEL_KEY
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_KEY=$OPENAI_KEY
AZURE_OPENAI_DEPLOYMENT=gpt-4
VALIDATION_SERVICE_URL=$FUNCTION_APP_URL
EOF

echo "✅ .env file created successfully!"

# Deploy Validation Service to Azure Functions
echo "⚡ Deploying Validation Service to Azure Functions..."
cd validation_service
func azure functionapp publish $FUNCTION_APP_NAME --python
cd ..

# Deploy SAP Simulator to Azure App Service
echo "🌐 Deploying SAP Simulator to Azure App Service..."
cd sap_simulator
az webapp up --name $WEB_APP_NAME --runtime "PYTHON:3.11" --sku B1
cd ..

echo "✨ Deployment completed successfully!"
echo ""
echo "📊 Deployment Summary:"
echo "===================="
cd terraform
terraform output

echo ""
echo "🌐 SAP Simulator:       $(terraform output -raw web_app_url)"
echo "⚡ Validation Function:  $(terraform output -raw function_app_url)"

echo ""
echo "💡 Next Steps:"
echo "1. Deploy a GPT-4 model in your Azure OpenAI resource"
echo "2. Update the AZURE_OPENAI_DEPLOYMENT environment variable with your deployment name"
echo "3. Visit the SAP Simulator URL to start validating documents"

cd ..
