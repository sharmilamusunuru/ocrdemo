# OCR Demo - SAP Delivery Quantity Validation

Azure-based SAP integration demo for validating delivery quantities from PDF documents using Azure AI services.

## Architecture

```
SAP Simulator (Flask, Port 5000)
    ├── Upload PDF → Azure Blob Storage (delivery-documents/{record_id}/raw/)
    ├── POST /api/validate → { record_id, delivery_quantity, blob_name }
    │
Validation Service (Azure Functions)
    ├── Read PDF from Blob Storage
    ├── Extract text via Azure Document Intelligence (prebuilt-document)
    ├── Match delivery_quantity against extracted quantities
    ├── Optional AI Agent validation (Azure OpenAI GPT-4)
    ├── Write result → {record_id}/processed/result.json
    └── Return JSON result to SAP
```

### Components

| Component | Technology | Azure Service |
|-----------|-----------|---------------|
| **SAP Simulator** | Flask web app | App Service |
| **Validation Service** | Azure Functions (v2 Python) | Azure Functions |
| **AI Agent** | OpenAI SDK | Azure OpenAI (GPT-4) |
| **Document OCR** | Form Recognizer SDK | Azure Document Intelligence |
| **Document Storage** | Blob SDK | Azure Blob Storage |

## Azure Services Required

- **Azure AI Document Intelligence** - OCR / text extraction from PDFs
- **Azure OpenAI Service (GPT-4)** - Intelligent validation and reasoning
- **Azure Blob Storage** - Document storage (`delivery-documents` container)
- **Azure App Service** - Hosts SAP Simulator
- **Azure Functions** - Hosts Validation Service

## Quick Start

```bash
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo

# Deploy infrastructure
cd terraform
terraform init && terraform plan && terraform apply

# Configure environment
cp .env.example .env
# Fill in values from Terraform outputs

# Deploy apps
./deploy.sh
```

## Project Structure

```
ocrdemo/
├── sap_simulator/
│   ├── app.py                  # Flask app (web UI + blob upload + API call)
│   ├── ai_agent.py             # AI agent module
│   ├── requirements.txt
│   └── templates/
│       └── sap_simulator.html  # Web UI
│
├── validation_service/
│   ├── function_app.py         # Azure Functions entry point (POST /api/validate)
│   ├── ai_agent.py             # AI validation logic
│   ├── host.json
│   └── requirements.txt
│
├── terraform/                  # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── deploy.sh                   # Automated deployment script
├── .env.example                # Environment variables template
└── README.md
```

## How It Works

1. User uploads a PDF and enters a delivery quantity in the **SAP Simulator** web UI
2. SAP Simulator uploads the PDF to Azure Blob Storage under `delivery-documents/{record_id}/raw/`
3. SAP Simulator calls `POST /api/validate` with `{ record_id, delivery_quantity, blob_name }`
4. Validation Service extracts text from the PDF using Azure Document Intelligence
5. Extracted quantities are matched against the provided `delivery_quantity`
6. If the AI Agent is enabled, Azure OpenAI provides additional validation with reasoning
7. Result JSON is written to `{record_id}/processed/result.json` and returned to the caller

## Environment Variables

```bash
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER_NAME=delivery-documents
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=...
AZURE_DOCUMENT_INTELLIGENCE_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4
VALIDATION_SERVICE_URL=http://localhost:7071  # SAP Simulator only
```

## Testing

1. Open the SAP Simulator at `http://localhost:5000`
2. Upload a PDF delivery document and enter the delivery quantity
3. Click **Save** — the result (match or mismatch) is displayed in the UI

## Author

Sharmila Musunuru