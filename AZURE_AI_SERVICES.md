# Azure AI Services - Required Services Guide

## 🎯 Overview

This document answers the key question: **What Azure AI services do I need for this solution?**

## ✅ Required Azure AI Services

### 1. Azure AI Document Intelligence (Form Recognizer)

**What it does:**
- Optical Character Recognition (OCR) from PDF documents
- Extracts text, tables, and structure from discharge documents
- Provides layout understanding and key-value pair extraction

**Is it required?**
✅ **YES** - This is the PRIMARY service for document processing

**Pricing:**
- **Free Tier**: 5,000 pages per month (perfect for testing)
- **S0 Tier**: Pay-per-page for production (~$1-10 per 1,000 pages)

**Service Type:**
- Azure Cognitive Services / Azure AI Services
- Category: Document Analysis

**API Used:**
- `azure-ai-formrecognizer` Python SDK
- REST API endpoint

---

### 2. Azure OpenAI Service (GPT-4)

**What it does:**
- Intelligent validation of quantities against document content
- Provides reasoning and confidence scores
- Context-aware analysis and decision making

**Is it required?**
✅ **YES** - This is the AI BRAIN for validation logic

**Pricing:**
- Pay-per-token (input + output)
- GPT-4: ~$0.03 per 1,000 input tokens, ~$0.06 per 1,000 output tokens
- Estimated cost for demo: $5-30/month (depends on usage)

**Model Deployment Required:**
- GPT-4 (version 0613 or later)
- Must deploy a model instance in Azure OpenAI Studio

**API Used:**
- `openai` Python SDK (configured for Azure)
- REST API endpoint

---

### 3. Azure Blob Storage

**What it does:**
- Stores uploaded PDF documents
- Provides secure, scalable document storage
- Integration point between SAP Simulator and Validation Service

**Is it required?**
✅ **YES** - Required for document storage

**Pricing:**
- Very low cost: ~$0.018 per GB per month
- Estimated cost for demo: $1-5/month

**Storage Type:**
- Standard LRS (Locally Redundant Storage) for demo
- Standard GRS (Geo-Redundant Storage) for production

---

### 4. Azure App Service or Azure Functions

**What it does:**
- Hosts the SAP Simulator web application
- Hosts the Validation Service API

**Is it required?**
✅ **YES** - Required to run the applications

**Options:**
1. **Azure App Service (Recommended for Demo)**
   - B1 tier: ~$13/month
   - Good for web UI (SAP Simulator)
   
2. **Azure Functions (Recommended for API)**
   - Consumption Plan: Pay-per-execution (~$0-5/month for demo)
   - Good for API backend (Validation Service)

---

## ❌ NOT Required

### Azure AI Foundry

**Do you need Azure AI Foundry?**
❌ **NO** - Azure AI Foundry is NOT required for this solution

**Why not?**
- Azure AI Document Intelligence handles document processing
- Azure OpenAI handles AI reasoning
- These two services provide everything needed
- AI Foundry is for more complex AI workflows and model management

---

## 📊 Summary: What You Need

| Service | Purpose | Required? | Estimated Cost (Demo) |
|---------|---------|-----------|----------------------|
| **Azure AI Document Intelligence** | OCR & Text Extraction | ✅ YES | Free tier or $1-10/month |
| **Azure OpenAI (GPT-4)** | AI Validation Logic | ✅ YES | $5-30/month |
| **Azure Blob Storage** | Document Storage | ✅ YES | $1-5/month |
| **Azure App Service** | Host SAP Simulator | ✅ YES | $13/month |
| **Azure Functions** | Host Validation API | ✅ YES | $0-5/month |
| **Azure AI Foundry** | N/A | ❌ NO | $0 |
| **Total Estimated Cost** | | | **$20-50/month** |

---

## 🚀 Quick Answer

### Is Document Intelligence enough?

**No, you need BOTH:**
1. **Azure AI Document Intelligence** - Extracts text from PDFs
2. **Azure OpenAI (GPT-4)** - Validates the extracted text with AI

Think of it this way:
- **Document Intelligence** = The "eyes" (reads the document)
- **Azure OpenAI** = The "brain" (understands and validates)

### Do I need Azure AI Foundry?

**No**, you do NOT need Azure AI Foundry. The combination of:
- Azure AI Document Intelligence +  
- Azure OpenAI

...provides everything you need for this solution.

---

## 🎯 Service Deployment Order

1. **First**: Deploy Azure infrastructure (Terraform)
   - Creates all required resources
   - Sets up storage, cognitive services, etc.

2. **Second**: Deploy GPT-4 model in Azure OpenAI
   ```bash
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

3. **Third**: Deploy applications
   ```bash
   ./deploy.sh
   ```

---

## 🔧 How Services Work Together

```
User Upload PDF
      ↓
Azure Blob Storage (stores PDF)
      ↓
Validation Service API (retrieves PDF)
      ↓
Azure AI Document Intelligence (extracts text)
      ↓
AI Agent Module (processes extracted text)
      ↓
Azure OpenAI GPT-4 (validates quantity)
      ↓
Return Result to User
```

---

## 💰 Cost Optimization Tips

### For Testing/Demo:
- ✅ Use Document Intelligence Free Tier (5,000 pages/month)
- ✅ Use Azure Functions Consumption Plan (pay per use)
- ✅ Use App Service B1 tier (lowest cost for always-on)
- ✅ Monitor OpenAI token usage to control costs

### For Production:
- Consider provisioned throughput for Azure OpenAI (predictable costs)
- Scale App Service to P-tier for better performance
- Use Premium Azure Functions for lower latency
- Enable Application Insights for monitoring

---

## 📋 Checklist: What to Deploy

Before you start, ensure you have access to create:
- [ ] Azure Cognitive Services (for Document Intelligence)
- [ ] Azure OpenAI Service (requires application approval)
- [ ] Azure Storage Account
- [ ] Azure App Service Plan
- [ ] Azure App Service or Azure Functions
- [ ] Resource Group

**Note**: Azure OpenAI may require approval in some regions. Apply early!

---

## 🌍 Regional Availability

**Important**: Not all services are available in all regions.

**Recommended Regions** (as of 2024):
- **East US** - All services available
- **West Europe** - All services available
- **UK South** - Most services available

Check availability:
```bash
# Check Azure OpenAI availability
az cognitiveservices account list-skus \
  --kind OpenAI \
  --location eastus

# Check Document Intelligence availability
az cognitiveservices account list-skus \
  --kind FormRecognizer \
  --location eastus
```

---

## 🔐 Required Permissions

You need permission to:
- Create Azure Resource Groups
- Create Azure Cognitive Services
- Create Azure Storage Accounts
- Create Azure App Services
- Deploy Azure OpenAI models
- Configure App Service settings

**Role Required**: Contributor or Owner on the subscription/resource group

---

## ❓ FAQ

### Q: Can I use Azure AI Search instead of Document Intelligence?
**A**: No, Azure AI Search is for searching across documents. You need Document Intelligence for OCR.

### Q: Can I use a different AI model instead of GPT-4?
**A**: Yes, you can use GPT-3.5-turbo for lower cost, but GPT-4 provides better reasoning.

### Q: What if I don't have access to Azure OpenAI?
**A**: You need to apply for Azure OpenAI access. It may take a few days to get approved.

### Q: Can I use OpenAI (non-Azure) instead of Azure OpenAI?
**A**: Technically yes, but the code uses Azure OpenAI SDK. You'd need to modify the code.

### Q: Is Azure AI Foundry the same as Azure AI Studio?
**A**: Azure AI Studio is the portal/UI. Azure AI Foundry is a newer offering. Neither is required for this solution.

---

## 📞 Next Steps

1. **Read** [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture
2. **Follow** [DEPLOYMENT.md](DEPLOYMENT.md) for deployment steps  
3. **Review** [FLOW_DIAGRAMS.md](FLOW_DIAGRAMS.md) for process flows

---

**Summary**: You need Azure AI Document Intelligence + Azure OpenAI. That's it! Azure AI Foundry is NOT required.
