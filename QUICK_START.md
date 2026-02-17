# Quick Start Guide - Azure Deployment

## 🎯 Azure AI Services Required

This solution requires the following Azure AI services:

### Core Services:
1. **Azure AI Document Intelligence** - For OCR and document text extraction
2. **Azure OpenAI Service (GPT-4)** - For intelligent validation and reasoning  
3. **Azure Blob Storage** - For document storage
4. **Azure App Service/Functions** - For hosting the applications

**Note:** Azure AI Foundry is NOT required. Azure AI Document Intelligence + Azure OpenAI is sufficient.

---

## 🚀 Getting Started
```bash
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo
./deploy.sh
# Follow prompts
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `deploy.sh` | Deploy to Azure |
| `DEPLOYMENT.md` | Azure deployment guide |
| `ARCHITECTURE.md` | Architecture and service mapping |
| `FLOW_DIAGRAMS.md` | System flow diagrams |
| `SOLUTION_SUMMARY.md` | Complete solution overview |

## 🏗️ Architecture

```
SAP Simulator (Port 5000)
    ↓ Upload PDF to storage
    ↓ Call API with quantity header
Validation Service (Port 5001)
    ↓ Read PDF from storage
    ↓ Extract text (OCR)
    ↓ Validate with AI
    ↓ Return result
```

## 🔧 Commands

### Azure Deployment
```bash
# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Deploy applications
cd ..
./deploy.sh
```

### Generate Test Documents
```bash
python create_sample_docs.py
# Creates: sample_discharge_document.pdf (qty: 1234.56)
#          sample_discharge_document_2.pdf (qty: 5678.90)
#          sample_discharge_document_3.pdf (qty: 100.00)
```

### Health Checks (Azure)
```bash
curl https://<your-app-name>.azurewebsites.net/health  # SAP Simulator
curl https://<validation-service>.azurewebsites.net/health  # Validation Service
```

### Test API Directly (Azure)
```bash
curl -X POST https://<validation-service>.azurewebsites.net/api/validate \
  -H "X-Discharge-Quantity: 1234.56" \
  -H "Content-Type: application/json" \
  -d '{"blob_name": "sample_discharge_document.pdf"}'
```

## 🌐 Azure Services

| Component | Service | Cost (Demo) |
|-----------|---------|-------------|
| SAP Simulator | App Service B1 | $13/mo |
| Validation API | Azure Functions | $0-5/mo |
| Document OCR | Document Intelligence | Free tier |
| AI Validation | Azure OpenAI (GPT-4) | $5-30/mo |
| Storage | Blob Storage | $1/mo |
| **Total** | | **~$20-50/mo** |

## 📝 Test Scenarios

### Successful Validation
1. Upload `sample_discharge_document.pdf`
2. Enter quantity: `1234.56`
3. Result: ✅ Validation Successful

### Failed Validation
1. Upload `sample_discharge_document.pdf`
2. Enter quantity: `9999.99`
3. Result: ❌ Validation Failed

## 🐛 Troubleshooting

### "Azure credentials not configured"
```bash
# Verify environment variables are set in Azure App Service
az webapp config appsettings list \
  --name <your-app-name> \
  --resource-group <your-rg>
```

### "Document Intelligence endpoint not responding"
```bash
# Verify resource is deployed
az cognitiveservices account show \
  --name <doc-intelligence-name> \
  --resource-group <your-rg>
```

### View Azure Logs
```bash
# Stream logs from App Service
az webapp log tail \
  --name <your-app-name> \
  --resource-group <your-rg>
```

## 📊 Directory Structure

```
ocrdemo/
├── sap_simulator/          # Frontend web app
│   ├── app.py             # Azure version
│   └── templates/         # HTML UI
├── validation_service/     # Backend API
│   ├── app.py             # Azure version
│   └── ai_agent.py        # AI validation module
├── terraform/              # Infrastructure as Code
│   ├── main.tf            # Resource definitions
│   ├── variables.tf       # Configuration
│   └── outputs.tf         # Deployment outputs
├── deploy.sh               # Azure deployment script
└── *.md                    # Documentation files
```

## 🔄 Workflow

### Deployment Flow
```
1. Code changes
2. Commit and push
3. Deploy infrastructure (terraform apply)
4. Deploy applications (./deploy.sh)
5. Test in Azure
6. Monitor with Application Insights
```

## 📖 Documentation Map

```
README.md              → Start here (overview)
├─ ARCHITECTURE.md     → Azure services & costs
├─ FLOW_DIAGRAMS.md    → How it works (diagrams)
├─ DEPLOYMENT.md       → Deploy to Azure
└─ SOLUTION_SUMMARY.md → Complete solution details
```

## 🎯 Use Cases

### For Development & Testing
- Deploy to Azure for testing with real AI services
- Use Azure's free tiers where available
- Test Document Intelligence OCR quality

### For Demonstration
- Deploy to Azure to show full AI features
- Demonstrate SAP integration pattern
- Show GPT-4 powered validation

### For Production
- Deploy to Azure with production SKUs
- Use real Document Intelligence
- Enable GPT-4 validation
- Add monitoring and scaling

## 💡 Tips

1. **Use Terraform for Infrastructure** - Consistent, repeatable deployments
2. **Use Sample Docs** - Pre-generated PDFs for quick testing
3. **Check Health Endpoints** - Verify services are running
4. **Read the Logs** - Azure logs show what's happening
5. **Enable Application Insights** - Monitor performance and errors
6. **Use Free Tiers** - Document Intelligence has a free tier for testing

## 🔗 Links

- [Azure Portal](https://portal.azure.com)
- [Azure CLI Docs](https://docs.microsoft.com/cli/azure/)
- [Terraform Docs](https://www.terraform.io/docs)
- [Flask Docs](https://flask.palletsprojects.com/)
- [Azure Document Intelligence](https://azure.microsoft.com/services/form-recognizer/)
- [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service)

## ❓ Need Help?

1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for Azure deployment issues
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design questions
3. See [FLOW_DIAGRAMS.md](FLOW_DIAGRAMS.md) to understand flow
4. Check Azure service health: https://status.azure.com/

## ✅ Quick Checklist

### Before Starting
- [ ] Azure subscription ready
- [ ] Python 3.11+ installed
- [ ] Azure CLI installed
- [ ] Terraform installed
- [ ] Git installed

### Azure Deployment
- [ ] Run `terraform init` and `terraform apply`
- [ ] Deploy GPT-4 model in Azure OpenAI
- [ ] Run `./deploy.sh`
- [ ] Configure environment variables
- [ ] Access https://<your-app>.azurewebsites.net
- [ ] Upload sample PDF
- [ ] Verify validation works

---

**Ready to get started? Follow the deployment steps in [DEPLOYMENT.md](DEPLOYMENT.md)!**
