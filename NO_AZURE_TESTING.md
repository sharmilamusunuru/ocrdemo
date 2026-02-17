# Testing Without Azure - Complete Guide

## TL;DR

**You can test the ENTIRE application locally WITHOUT any Azure services, credentials, or deployments!**

```bash
# Just run this - no Azure needed!
./start_local.sh
```

## Three Testing Modes

### Mode 1: Fully Local (Recommended for Testing) ✅

**What you need:**
- Python 3.11+
- (Optional) Tesseract OCR

**What you DON'T need:**
- ❌ No Azure subscription
- ❌ No Azure credentials
- ❌ No Document Intelligence
- ❌ No Azure OpenAI
- ❌ No Blob Storage
- ❌ No infrastructure deployment

**How it works:**
- Uses `app_local.py` files
- Stores files on local filesystem
- Uses Tesseract OCR (free, open-source)
- Uses mock AI responses
- No external dependencies

**Start testing:**
```bash
./start_local.sh
# Open http://localhost:5000
# Upload PDF, enter quantity, see results!
```

### Mode 2: Hybrid (Azure Services Optional)

**What you need:**
- Azure subscription (if you want to test specific Azure services)
- Only the services you want to test

**Options:**
1. **Test with Document Intelligence only** (no AI):
   ```bash
   # Deploy just Document Intelligence
   # Add credentials to .env
   # Uses real OCR, mock AI
   ```

2. **Test with Azure OpenAI only** (no Document Intelligence):
   ```bash
   # Deploy just OpenAI
   # Add credentials to .env
   # Uses Tesseract OCR, real AI
   ```

3. **Test with both** (full Azure AI):
   ```bash
   # Deploy both services
   # Full Azure experience locally
   ```

### Mode 3: Fully Azure

**What you need:**
- Complete Azure infrastructure
- All credentials configured

**Use case:**
- Production testing
- Performance testing
- Full integration testing

## Detailed: Mode 1 - Fully Local (No Azure)

### Step 1: Install Dependencies

```bash
# Clone repo
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo

# Install Python dependencies
cd sap_simulator
pip install -r requirements.txt

cd ../validation_service  
pip install -r requirements.txt
pip install pytesseract pillow pdf2image  # For local OCR

# Install Tesseract (OPTIONAL - only for OCR)
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Step 2: Start Services

**Option A: Automatic (Recommended)**
```bash
./start_local.sh
```

**Option B: Manual**
```bash
# Terminal 1: Validation Service
cd validation_service
python app_local.py
# Runs on http://localhost:5001

# Terminal 2: SAP Simulator
cd sap_simulator
python app_local.py
# Runs on http://localhost:5000
```

**Option C: Docker**
```bash
docker-compose up
```

### Step 3: Test

```bash
# Generate sample PDFs
python create_sample_docs.py

# Open browser
# http://localhost:5000

# Upload sample_discharge_document.pdf
# Enter quantity: 1234.56
# Click "Save"
# See: ✅ Validation Successful!
```

## What Happens in Local Mode

### File Upload Flow
```
1. User uploads PDF via web UI
   ↓
2. SAP Simulator saves to ./local_storage/documents/
   (NOT Azure Blob Storage)
   ↓
3. Calls local Validation Service API
   ↓
4. Validation Service reads from ./local_storage/documents/
   ↓
5. Uses Tesseract OCR to extract text
   (NOT Azure Document Intelligence)
   ↓
6. Extracts numbers with regex
   ↓
7. Returns mock AI validation response
   (NOT Azure OpenAI)
   ↓
8. UI displays result
```

### Local Replacements

| Azure Service | Local Replacement | Quality |
|---------------|-------------------|---------|
| Blob Storage | Local filesystem (`./local_storage/`) | ✅ Same for testing |
| Document Intelligence | Tesseract OCR | ⚠️ Good enough for testing |
| Azure OpenAI | Mock responses | ✅ Perfect for testing logic |

## Without Tesseract (Minimal Setup)

If you don't install Tesseract, the app still works but with limited OCR:

```python
# In validation_service/app_local.py
# It will return a message: "Tesseract not available"
# But the rest of the app still functions
```

To test **without** OCR, you can:
1. Use pre-extracted text (hardcoded)
2. Skip OCR and just test validation logic
3. Install Tesseract later when needed

## Common Questions

### Q: Do I need an Azure account?
**A: No!** Local mode works without any Azure account.

### Q: Do I need to deploy infrastructure?
**A: No!** Infrastructure is only for Azure deployment.

### Q: Do I need Document Intelligence keys?
**A: No!** Local mode uses Tesseract OCR.

### Q: Do I need OpenAI API keys?
**A: No!** Local mode uses mock AI responses.

### Q: Will it work on my laptop?
**A: Yes!** Works on Windows, Mac, Linux.

### Q: What's the difference from Azure version?
**A: Azure version uses cloud AI services. Local version uses free alternatives. Results are similar for testing.**

### Q: Can I deploy later?
**A: Yes!** Develop locally, deploy to Azure when ready.

## Verify It's Working

### Health Checks
```bash
# Check Validation Service
curl http://localhost:5001/health

# Expected response:
{
  "status": "healthy",
  "service": "Validation Service (Local Mode)",
  "mode": "local",
  "tesseract_available": true,
  "storage_path": "./local_storage/documents"
}

# Check SAP Simulator
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "service": "SAP Simulator (Local Mode)",
  "mode": "local",
  "storage_path": "./local_storage/documents",
  "validation_service_reachable": true
}
```

### Test Validation API
```bash
# First, copy a sample PDF to local storage
mkdir -p local_storage/documents
cp sample_discharge_document.pdf local_storage/documents/test.pdf

# Call validation API
curl -X POST http://localhost:5001/api/validate \
  -H "X-Discharge-Quantity: 1234.56" \
  -H "Content-Type: application/json" \
  -d '{"blob_name": "test.pdf"}'

# Should return validation result!
```

## When To Use Azure

**Use Local Mode When:**
- ✅ Developing features
- ✅ Testing logic
- ✅ Learning the system
- ✅ Quick iterations
- ✅ No internet/Azure access
- ✅ Want to save costs

**Use Azure Mode When:**
- ✅ Need production-quality OCR
- ✅ Want AI-powered validation
- ✅ Demonstrating to stakeholders
- ✅ Performance testing
- ✅ Integration testing
- ✅ Production deployment

## Troubleshooting Local Mode

### "Connection refused"
```bash
# Make sure Validation Service is running
cd validation_service
python app_local.py

# Then start SAP Simulator
cd sap_simulator
python app_local.py
```

### "Tesseract not found"
```bash
# Option 1: Install Tesseract (recommended)
sudo apt-get install tesseract-ocr  # Linux
brew install tesseract               # macOS

# Option 2: Continue without OCR
# The app will still run, just with limited text extraction
```

### "Module not found"
```bash
# Install dependencies
cd sap_simulator
pip install -r requirements.txt

cd ../validation_service
pip install -r requirements.txt
pip install pytesseract pillow pdf2image
```

### "Port already in use"
```bash
# Find and kill process using port 5000 or 5001
lsof -ti:5000 | xargs kill -9
lsof -ti:5001 | xargs kill -9

# Or use different ports
# Edit app_local.py and change port numbers
```

## Testing Scenarios (No Azure)

### Scenario 1: Basic Validation
```bash
1. Start services: ./start_local.sh
2. Open: http://localhost:5000
3. Upload: sample_discharge_document.pdf
4. Enter: 1234.56
5. Click: Save
6. Result: ✅ Validation Successful
```

### Scenario 2: Failed Validation
```bash
1. Open: http://localhost:5000
2. Upload: sample_discharge_document.pdf
3. Enter: 9999.99 (wrong quantity)
4. Click: Save
5. Result: ❌ Validation Failed
```

### Scenario 3: Different Document
```bash
1. Upload: sample_discharge_document_2.pdf
2. Enter: 5678.90
3. Result: ✅ Validation Successful
```

### Scenario 4: API Testing
```bash
# Direct API call
curl -X POST http://localhost:5001/api/validate \
  -H "X-Discharge-Quantity: 1234.56" \
  -H "Content-Type: application/json" \
  -d '{"blob_name": "20240217_123456_abc123_sample.pdf"}'
```

## Comparison Table

| Feature | Local (No Azure) | Azure (Full) |
|---------|------------------|--------------|
| **Setup Time** | 2 minutes | 30-60 minutes |
| **Cost** | Free | $20-50/month |
| **OCR Quality** | Good (Tesseract) | Excellent (Document Intelligence) |
| **AI Quality** | Mock (rule-based) | Real (GPT-4) |
| **Speed** | Very fast | Network latency |
| **Internet** | Not required | Required |
| **Azure Account** | Not required | Required |
| **Use Case** | Development, Testing | Demo, Production |

## Next Steps

### After Local Testing Works

1. **Deploy to Azure** (when ready):
   ```bash
   cd terraform
   terraform apply
   ```

2. **Get Azure credentials**:
   ```bash
   terraform output
   ```

3. **Test with Azure services**:
   ```bash
   # Use app.py instead of app_local.py
   # Add Azure credentials to .env
   # Deploy to App Service
   ```

4. **Compare results**:
   - Local OCR vs Document Intelligence
   - Mock AI vs Real GPT-4
   - See the difference!

## Summary

✅ **You can test everything locally without Azure**  
✅ **No infrastructure deployment needed**  
✅ **No Azure credentials required**  
✅ **No costs involved**  
✅ **Perfect for development and testing**  

When you're ready for production-quality AI and OCR, deploy to Azure!

---

**Just run `./start_local.sh` and start testing!**
