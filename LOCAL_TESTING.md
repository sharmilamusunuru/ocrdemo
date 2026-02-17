# Local Development and Testing Guide

This guide shows you how to test the OCR Demo application locally **without** requiring Azure resources.

## Quick Start (Local Testing)

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- (Optional) Docker for containerized testing

### Option 1: Local Testing with Mock Services (Recommended)

This approach uses local file storage and mock AI services, perfect for testing the application flow without Azure.

#### Step 1: Install Dependencies

```bash
# Install SAP Simulator dependencies
cd sap_simulator
pip install -r requirements.txt
pip install python-multipart  # For file uploads

# Install Validation Service dependencies
cd ../validation_service
pip install -r requirements.txt
```

#### Step 2: Set Up Local Configuration

Create a `.env.local` file in the project root:

```bash
# Local development configuration
MODE=local
LOCAL_STORAGE_PATH=./local_storage/documents
VALIDATION_SERVICE_URL=http://localhost:5001

# Optional: Add real Azure credentials if you want to test with real services
# AZURE_STORAGE_CONNECTION_STRING=...
# AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=...
# AZURE_DOCUMENT_INTELLIGENCE_KEY=...
# AZURE_OPENAI_ENDPOINT=...
# AZURE_OPENAI_KEY=...
```

#### Step 3: Create Local Storage Directory

```bash
mkdir -p local_storage/documents
```

#### Step 4: Run Validation Service (Backend)

```bash
cd validation_service
python app_local.py  # Uses local mode
```

The service will start on `http://localhost:5001`

#### Step 5: Run SAP Simulator (Frontend)

In a new terminal:

```bash
cd sap_simulator
python app_local.py  # Uses local mode
```

The simulator will start on `http://localhost:5000`

#### Step 6: Test the Application

1. Open browser: `http://localhost:5000`
2. Generate test documents:
   ```bash
   python create_sample_docs.py
   ```
3. Upload `sample_discharge_document.pdf`
4. Enter quantity: `1234.56`
5. Click "Save (Upload to Blob & Validate)"
6. See results!

### Option 2: Docker Compose (Containerized)

Run both services in Docker containers:

```bash
# Build and start services
docker-compose up

# Access at http://localhost:5000
```

### Option 3: Hybrid Testing (Local + Real Azure Services)

Test locally but use real Azure services for AI:

1. Set up Azure resources (just the AI services)
2. Add credentials to `.env.local`
3. Run locally with real AI validation

```bash
# .env.local with real Azure services
MODE=hybrid
LOCAL_STORAGE_PATH=./local_storage/documents
VALIDATION_SERVICE_URL=http://localhost:5001

# Real Azure credentials for AI services
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

## Local Mode Features

### What Works Locally:
✅ Full web UI for SAP Simulator  
✅ File upload and storage  
✅ API calls between services  
✅ Document text extraction (using pytesseract as fallback)  
✅ Quantity validation logic  
✅ Mock AI responses (when Azure not configured)  
✅ Success/failure result display  

### Limitations in Local Mode:
❌ No real Azure Blob Storage (uses local filesystem)  
❌ No Azure Document Intelligence (uses Tesseract OCR fallback)  
❌ No real AI Agent (uses mock responses or simple validation)  
❌ No Azure authentication/security  

## Testing Scenarios

### Test 1: Successful Validation
```bash
# Upload sample_discharge_document.pdf
# Enter quantity: 1234.56
# Expected: ✅ Validation Successful
```

### Test 2: Failed Validation
```bash
# Upload sample_discharge_document.pdf
# Enter quantity: 9999.99
# Expected: ❌ Validation Failed
```

### Test 3: Different Document
```bash
# Upload sample_discharge_document_2.pdf
# Enter quantity: 5678.90
# Expected: ✅ Validation Successful
```

### Test 4: API Direct Call
```bash
# Test validation API directly
curl -X POST http://localhost:5001/api/validate \
  -H "X-Discharge-Quantity: 1234.56" \
  -H "Content-Type: application/json" \
  -d '{"blob_name": "sample_discharge_document.pdf"}'
```

### Test 5: Health Checks
```bash
# Check SAP Simulator
curl http://localhost:5000/health

# Check Validation Service
curl http://localhost:5001/health
```

## Debugging

### Enable Debug Mode

```bash
# In app_local.py files, Flask runs with debug=True by default
# View detailed error messages in browser and console
```

### View Logs

```bash
# Both services output logs to console
# Watch for errors in the terminal where services are running
```

### Common Issues

**Issue**: "Connection refused to localhost:5001"
```bash
# Solution: Make sure Validation Service is running first
cd validation_service && python app_local.py
```

**Issue**: "Module not found"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: "Tesseract not found"
```bash
# Solution: Install Tesseract OCR (for local testing)
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

**Issue**: "No quantities extracted"
```bash
# Solution: Ensure PDF has clear, readable text
# Try with the generated sample documents first
```

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Linux
brew install ab  # macOS

# Test validation endpoint
ab -n 100 -c 10 http://localhost:5001/health
```

### Test with Multiple Files

```bash
# Upload multiple documents concurrently
for i in {1..10}; do
  curl -X POST http://localhost:5000/simulate-sap \
    -F "document=@sample_discharge_document.pdf" \
    -F "quantity=1234.56" &
done
wait
```

## Transition to Azure

Once local testing is complete:

1. **Deploy Infrastructure**:
   ```bash
   cd terraform
   terraform apply
   ```

2. **Update Environment Variables**:
   - Replace local paths with Azure blob URLs
   - Add Azure service credentials

3. **Deploy Applications**:
   ```bash
   ./deploy.sh
   ```

4. **Test on Azure**:
   - Access via `https://<your-app>.azurewebsites.net`
   - Verify Azure services integration

## Development Workflow

```
1. Code changes → Test locally → Verify works
2. Commit changes → Push to Git
3. Deploy to Azure → Test in cloud
4. Monitor → Iterate
```

## VS Code Configuration

Create `.vscode/launch.json` for debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "SAP Simulator",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/sap_simulator/app_local.py",
      "console": "integratedTerminal",
      "env": {
        "FLASK_ENV": "development"
      }
    },
    {
      "name": "Validation Service",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/validation_service/app_local.py",
      "console": "integratedTerminal",
      "env": {
        "FLASK_ENV": "development"
      }
    }
  ],
  "compounds": [
    {
      "name": "Full App",
      "configurations": ["Validation Service", "SAP Simulator"]
    }
  ]
}
```

## Next Steps

- ✅ Test locally with mock services
- ✅ Verify all functionality works
- ✅ Fix any issues in local environment
- ✅ Deploy to Azure when ready
- ✅ Compare local vs Azure behavior
- ✅ Optimize based on real Azure performance

## Tips for Local Development

1. **Start Validation Service First**: Always start the backend before the frontend
2. **Use Sample Documents**: Generate test PDFs with `create_sample_docs.py`
3. **Check Logs**: Watch console output for errors
4. **Test Incrementally**: Test each component separately before integration
5. **Mock AI Responses**: Use hardcoded responses to test UI without AI services
6. **Hot Reload**: Flask's debug mode auto-reloads on code changes

## Mock vs Real Services Comparison

| Feature | Local (Mock) | Azure (Real) |
|---------|--------------|--------------|
| Storage | Local filesystem | Azure Blob Storage |
| OCR | Tesseract | Document Intelligence |
| AI Validation | Rule-based | GPT-4 powered |
| Cost | Free | Pay per use |
| Performance | Fast | Network latency |
| Scalability | Limited | Auto-scaling |
| Production Ready | No | Yes |

For development and testing, local mode is perfect. For demos and production, use Azure.
