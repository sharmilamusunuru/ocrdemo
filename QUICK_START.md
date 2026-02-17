# Quick Reference Guide

## 🎯 NO AZURE NEEDED FOR TESTING!

**You can test the entire application locally without ANY Azure services!**

```bash
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo
./start_local.sh
# Open http://localhost:5000
```

**What you DON'T need:**
- ❌ No Azure subscription
- ❌ No Azure credentials  
- ❌ No Document Intelligence keys
- ❌ No OpenAI API keys
- ❌ No infrastructure deployment
- ❌ No costs!

**See [NO_AZURE_TESTING.md](NO_AZURE_TESTING.md) for complete details**

---

## 🚀 Getting Started

### Option 1: Local Testing (Fastest - No Azure needed!)
```bash
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo
./start_local.sh
# Open http://localhost:5000
```

### Option 2: Azure Deployment (Production-ready)
```bash
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo
./deploy.sh
# Follow prompts
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `start_local.sh` | Start app locally (no Azure) |
| `deploy.sh` | Deploy to Azure |
| `LOCAL_TESTING.md` | Local development guide |
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

### Local Development
```bash
# Start both services
./start_local.sh

# Or manually:
cd validation_service && python app_local.py &  # Port 5001
cd sap_simulator && python app_local.py &       # Port 5000

# Using Docker
docker-compose up
```

### Generate Test Documents
```bash
python create_sample_docs.py
# Creates: sample_discharge_document.pdf (qty: 1234.56)
#          sample_discharge_document_2.pdf (qty: 5678.90)
#          sample_discharge_document_3.pdf (qty: 100.00)
```

### Health Checks
```bash
curl http://localhost:5000/health  # SAP Simulator
curl http://localhost:5001/health  # Validation Service
```

### Test API Directly
```bash
curl -X POST http://localhost:5001/api/validate \
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

### "Connection refused to localhost:5001"
```bash
# Start Validation Service first
cd validation_service && python app_local.py
```

### "Tesseract not found"
```bash
# Linux
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler

# Then restart services
```

### "Module not found"
```bash
cd sap_simulator && pip install -r requirements.txt
cd ../validation_service && pip install -r requirements.txt
```

### View Logs
```bash
# Logs appear in the terminal where services are running
# Watch for errors in console output
```

## 📊 Directory Structure

```
ocrdemo/
├── sap_simulator/          # Frontend web app
│   ├── app.py             # Azure version
│   ├── app_local.py       # Local version (no Azure)
│   └── templates/         # HTML UI
├── validation_service/     # Backend API
│   ├── app.py             # Azure version
│   ├── app_local.py       # Local version (no Azure)
│   └── ai_agent.py        # AI validation module
├── terraform/              # Infrastructure as Code
│   ├── main.tf            # Resource definitions
│   ├── variables.tf       # Configuration
│   └── outputs.tf         # Deployment outputs
├── start_local.sh          # Local startup script
├── deploy.sh               # Azure deployment script
├── docker-compose.yml      # Docker setup
└── *.md                    # Documentation files
```

## 🔄 Workflow

### Development Flow
```
1. Code changes
2. Test locally (./start_local.sh)
3. Verify functionality
4. Commit and push
5. Deploy to Azure (./deploy.sh)
6. Test in cloud
```

### Local → Azure Migration
```
1. Develop locally with app_local.py
2. Test with local OCR
3. Deploy infrastructure (terraform apply)
4. Switch to app.py with Azure services
5. Test with real Document Intelligence & GPT-4
6. Compare results
```

## 📖 Documentation Map

```
README.md              → Start here (overview)
├─ LOCAL_TESTING.md    → Local development guide
├─ ARCHITECTURE.md     → Azure services & costs
├─ FLOW_DIAGRAMS.md    → How it works (diagrams)
├─ DEPLOYMENT.md       → Deploy to Azure
└─ SOLUTION_SUMMARY.md → Complete solution details
```

## 🎯 Use Cases

### For Development
- Use local mode (`app_local.py`)
- Free, fast iteration
- No Azure costs

### For Demonstration
- Use local mode for quick demos
- Or deploy to Azure for full AI features
- Show SAP integration pattern

### For Production
- Deploy to Azure
- Use real Document Intelligence
- Enable GPT-4 validation
- Add monitoring and scaling

## 💡 Tips

1. **Start Local First** - Always test locally before Azure
2. **Use Sample Docs** - Pre-generated PDFs for quick testing
3. **Check Health Endpoints** - Verify services are running
4. **Read the Logs** - Console output shows what's happening
5. **One Service at a Time** - Start validation service first
6. **Docker for Clean State** - Use Docker Compose for isolated testing

## 🔗 Links

- [Azure Portal](https://portal.azure.com)
- [Azure CLI Docs](https://docs.microsoft.com/cli/azure/)
- [Terraform Docs](https://www.terraform.io/docs)
- [Flask Docs](https://flask.palletsprojects.com/)
- [Azure Document Intelligence](https://azure.microsoft.com/services/form-recognizer/)
- [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service)

## ❓ Need Help?

1. Check [LOCAL_TESTING.md](LOCAL_TESTING.md) for local issues
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for Azure issues
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design questions
4. See [FLOW_DIAGRAMS.md](FLOW_DIAGRAMS.md) to understand flow

## ✅ Quick Checklist

### Before Starting
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] (Optional) Tesseract for local OCR
- [ ] (Optional) Docker for containerized testing

### Local Testing
- [ ] Run `./start_local.sh`
- [ ] Access http://localhost:5000
- [ ] Upload sample PDF
- [ ] Verify validation works

### Azure Deployment
- [ ] Azure subscription ready
- [ ] Azure CLI installed
- [ ] Terraform installed
- [ ] Run `./deploy.sh`
- [ ] Configure OpenAI deployment
- [ ] Test in cloud

---

**Ready to get started? Run `./start_local.sh` and open http://localhost:5000!**
