# OCR Demo - SAP Discharge Quantity Validation

A comprehensive demonstration of SAP-to-Azure integration for validating discharge quantities using Azure AI services.

## 🎯 Purpose

This application demonstrates how SAP systems can integrate with Azure to validate discharge quantities from PDF documents using:
- **Azure Document Intelligence** for OCR
- **Azure OpenAI (GPT-4)** for intelligent validation
- **Azure Blob Storage** for document storage

## 🏗️ Architecture

This solution consists of two main components:

### 1. **SAP Simulator** (Dummy App)
- Mimics SAP behavior in the customer scenario
- Provides web UI for document upload and quantity entry
- Uploads PDFs to Azure Blob Storage
- Calls validation API with quantity in header
- **Azure Service**: App Service (Web App)

### 2. **Validation Service** (API Backend)
- REST API that validates quantities against documents
- Reads PDFs from Blob Storage
- Extracts text using Azure Document Intelligence
- Uses AI Agent with GPT-4 for validation
- **Azure Service**: Azure Functions (Recommended) or App Service

### 3. **AI Agent**
- Intelligent validation logic using Azure OpenAI
- Context-aware quantity matching
- Provides confidence scores and reasoning
- **Azure Service**: Azure OpenAI (GPT-4)

## 📋 Documentation

- **[AZURE_AI_SERVICES.md](AZURE_AI_SERVICES.md)** - **READ THIS FIRST**: Which Azure AI services you need (Document Intelligence vs AI Foundry)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture, components, and Azure service recommendations
- **[FLOW_DIAGRAMS.md](FLOW_DIAGRAMS.md)** - System flow diagrams and sequence diagrams
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Step-by-step deployment instructions

## ☁️ Azure AI Services Required

This solution uses the following Azure AI services:

### Required Services:
1. **Azure AI Document Intelligence** (Form Recognizer)
   - Purpose: OCR and text extraction from PDF documents
   - Tier: Free tier available (5,000 pages/month) or S0 for production
   - **This is the primary AI service for document processing**

2. **Azure OpenAI Service** (GPT-4)
   - Purpose: Intelligent validation and reasoning
   - Model: GPT-4 deployment required
   - **This provides AI-powered validation logic**

3. **Azure Blob Storage**
   - Purpose: Secure document storage
   - Tier: Standard LRS for demo, GRS for production

4. **Azure App Service** or **Azure Functions**
   - Purpose: Host SAP Simulator and Validation Service
   - Tier: B1 for demo, P1V2 for production

### Is Azure AI Document Intelligence Enough?

**Answer: You need BOTH Azure AI Document Intelligence AND Azure OpenAI Service**

- **Azure AI Document Intelligence**: Extracts text and structure from PDFs (OCR)
- **Azure OpenAI (GPT-4)**: Performs intelligent validation and reasoning on the extracted text

**Azure AI Foundry is NOT required** for this solution. The combination of Document Intelligence and Azure OpenAI provides everything needed.

## 🚀 Quick Start - Azure Deployment

### Prerequisites

1. **Azure Subscription** with access to:
   - Azure App Service
   - Azure Functions
   - Azure Blob Storage
   - Azure AI Document Intelligence
   - Azure OpenAI Service

2. **Local Development Tools**:
   - Python 3.11+
   - Azure CLI
   - Terraform (for infrastructure deployment)

### Deployment Steps

1. **Clone the repository**:
```bash
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo
```

2. **Deploy Azure Infrastructure**:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

3. **Configure Environment Variables**:
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your Azure credentials
# (These will be output from Terraform)
```

4. **Deploy Applications**:

**Option 1: Automated Deployment**
```bash
./deploy.sh
```

**Option 2: Manual Deployment**
```bash
# Deploy SAP Simulator to App Service
cd sap_simulator
az webapp up --name <your-app-name> --runtime "PYTHON:3.11"

# Deploy Validation Service to Azure Functions
cd validation_service
func azure functionapp publish <your-function-app-name>
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

5. **Configure Azure OpenAI**:
```bash
# Create GPT-4 deployment in Azure OpenAI Studio
# Or use Azure CLI:
az cognitiveservices account deployment create \
  --name <your-openai-resource> \
  --resource-group <your-rg> \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

6. **Access the Application**:
```
Open browser: https://<your-app-name>.azurewebsites.net
```

## 📁 Project Structure

```
ocrdemo/
├── sap_simulator/              # SAP simulation web app
│   ├── app.py                  # Flask application
│   ├── templates/              # HTML templates
│   │   └── sap_simulator.html  # Web UI
│   └── ai_agent.py            # Shared AI agent module
│
├── validation_service/         # Validation API service
│   ├── app.py                  # REST API endpoints
│   └── ai_agent.py            # AI validation logic
│
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                # Azure resources definition
│   ├── variables.tf           # Configuration variables
│   └── outputs.tf             # Deployment outputs
│
├── ai_agent.py                # Core AI agent module
├── create_sample_docs.py      # Generate test PDFs
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── deploy.sh                 # Automated deployment script
│
├── README.md                  # This file
├── ARCHITECTURE.md           # Architecture documentation
├── FLOW_DIAGRAMS.md         # System flow diagrams
└── DEPLOYMENT.md            # Deployment guide
```

## 🔄 How It Works

### Customer Scenario (Production)
1. SAP system uploads discharge document to Azure Blob Storage
2. SAP calls Azure Validation API with quantity in header
3. API reads document from blob storage
4. Azure Document Intelligence extracts text from PDF
5. AI Agent (GPT-4) validates quantity against document content
6. API returns validation result to SAP

### Demo Scenario (This Implementation)
1. User uploads PDF and enters quantity in **SAP Simulator** web UI
2. SAP Simulator uploads PDF to Azure Blob Storage
3. SAP Simulator calls **Validation Service** API
4. Validation Service processes document with Azure Document Intelligence
5. AI Agent validates using GPT-4
6. Result displayed in SAP Simulator UI

## 🎨 Features

- ✅ **Web UI** - User-friendly interface simulating SAP
- ✅ **Azure Blob Storage** - Secure document storage
- ✅ **Azure Document Intelligence** - Advanced OCR capabilities
- ✅ **AI-Powered Validation** - GPT-4 for context-aware validation
- ✅ **REST API** - Clean API design matching customer scenario
- ✅ **Infrastructure as Code** - Terraform for repeatable deployments
- ✅ **Confidence Scoring** - AI provides validation confidence levels
- ✅ **Detailed Reasoning** - AI explains validation decisions

## 🧪 Testing

1. **Generate Sample Documents**:
```bash
python create_sample_docs.py
```

2. **Test with Sample Document**:
   - Upload `sample_discharge_document.pdf`
   - Enter quantity: `1234.56`
   - Click "Save"
   - Should return: **Validation Successful**

3. **Test Failure Case**:
   - Upload same document
   - Enter quantity: `9999.99`
   - Should return: **Validation Failed**

## 💰 Cost Estimate

### Demo/Development:
- **Total**: ~$20-50/month
  - App Service (B1): ~$13/month
  - Azure Functions (Consumption): ~$0-5/month
  - Document Intelligence (Free tier): $0
  - Blob Storage: ~$1/month
  - Azure OpenAI (pay-per-use): ~$5-30/month

### Production:
- **Total**: ~$200-500/month (depends on volume)
  - See [ARCHITECTURE.md](ARCHITECTURE.md) for details

## 🔒 Security Considerations

- ✅ Environment variables for all secrets
- ✅ Azure Managed Identities (recommended for production)
- ✅ Blob storage with private access
- ✅ API authentication (add API Management in production)
- ✅ TLS/HTTPS for all communication
- ✅ Input validation and sanitization

## 📊 Monitoring

Add Application Insights to monitor:
- API response times
- Document processing success rates
- AI validation accuracy
- Error rates and exceptions

```bash
# Enable Application Insights
az monitor app-insights component create \
  --app <app-name> \
  --location <location> \
  --resource-group <rg-name>
```

## 🤝 Contributing

This is a demonstration project. For production use:
1. Add comprehensive error handling
2. Implement API authentication (OAuth 2.0)
3. Add monitoring and alerting
4. Set up CI/CD pipelines
5. Implement database for audit trails
6. Add API Management for governance

## 📄 License

MIT License

## 👤 Author

Sharmila Musunuru

## 🔗 Related Documentation

- [Azure Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/)
- [Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/)
- [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/)