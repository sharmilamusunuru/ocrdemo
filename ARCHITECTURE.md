# Azure Architecture and Deployment Guide

## Overview

This solution demonstrates a SAP-to-Azure integration pattern for discharge quantity validation using AI and Document Intelligence.

## Architecture Components

### 1. SAP Simulator (Frontend Application)
**What it is:** A web application that mimics SAP's behavior
**Technology:** Flask web application
**Azure Service:** **Azure App Service (Web App)**
**Why App Service:**
- Simple Python web hosting
- Built-in scaling
- Easy CI/CD integration
- Good for interactive web UIs
- Support for custom domains and SSL

**Files:**
- `sap_simulator/app.py` - Flask application
- `sap_simulator/templates/sap_simulator.html` - Web UI
- `sap_simulator/ai_agent.py` - Shared AI agent module

### 2. Validation Service (Backend API)
**What it is:** API service that validates quantities against documents
**Technology:** Flask REST API
**Azure Service:** **Azure Functions (Consumption Plan)** or **Azure App Service (API App)**

**Recommendation: Azure Functions**
**Why Azure Functions:**
- Event-driven, serverless architecture
- Pay-per-execution pricing
- Auto-scaling based on demand
- Perfect for API endpoints
- Built-in API Management integration
- Lower cost for intermittent workloads

**Alternative: Azure App Service if:**
- Need always-on availability
- Expect high, consistent traffic
- Need more control over runtime environment

**Files:**
- `validation_service/app.py` - REST API endpoints
- `validation_service/ai_agent.py` - AI validation logic

### 3. AI Agent (Intelligence Layer)
**What it is:** AI-powered validation logic using Azure OpenAI
**Technology:** Python module using Azure OpenAI SDK
**Azure Service:** **Azure OpenAI Service** (GPT-4)
**Integration:** Embedded within Validation Service

**Why Azure OpenAI:**
- Advanced reasoning capabilities
- Context understanding for validation
- Confidence scoring
- Enterprise-grade security
- Microsoft support

**Files:**
- `ai_agent.py` - Core AI logic module

### 4. Document Processing
**Azure Service:** **Azure AI Document Intelligence** (Form Recognizer)
**Purpose:** Extract text and structure from PDFs
**Why Document Intelligence:**
- Pre-built OCR capabilities
- Layout understanding
- Key-value pair extraction
- Better than basic OCR for documents
- Handles complex layouts

### 5. Storage Layer
**Azure Service:** **Azure Blob Storage**
**Purpose:** Store uploaded PDF documents
**Why Blob Storage:**
- Cost-effective for file storage
- Secure with SAS tokens
- Integration with all Azure services
- Lifecycle management
- Redundancy options

### 6. Infrastructure as Code
**Technology:** **Terraform**
**Files:**
- `terraform/main.tf` - Infrastructure definition
- `terraform/variables.tf` - Configuration variables
- `terraform/outputs.tf` - Deployment outputs

## Architecture Layers

### Presentation Layer
```
┌─────────────────────────────────────┐
│   SAP Simulator (Web UI)            │
│   Azure App Service                 │
│                                     │
│   Files:                            │
│   - sap_simulator/app.py            │
│   - sap_simulator/templates/*.html  │
└─────────────────────────────────────┘
```

### API Layer
```
┌─────────────────────────────────────┐
│   Validation Service API            │
│   Azure Functions                   │
│                                     │
│   Files:                            │
│   - validation_service/app.py       │
│   Endpoints:                        │
│   - POST /api/validate              │
│   - POST /api/analyze-structure     │
│   - GET /health                     │
└─────────────────────────────────────┘
```

### Business Logic Layer
```
┌─────────────────────────────────────┐
│   AI Agent Module                   │
│   Integrated in Validation Service  │
│                                     │
│   Files:                            │
│   - ai_agent.py                     │
│   Class: ValidationAgent            │
│   Methods:                          │
│   - validate()                      │
│   - analyze_document_structure()    │
└─────────────────────────────────────┘
```

### AI Services Layer
```
┌─────────────────────────────────────┐
│   Azure OpenAI Service              │
│   - GPT-4 Deployment                │
│                                     │
│   Azure Document Intelligence       │
│   - Prebuilt Document Model         │
└─────────────────────────────────────┘
```

### Data Layer
```
┌─────────────────────────────────────┐
│   Azure Blob Storage                │
│   Container: discharge-documents    │
│   - PDF documents                   │
│   - Metadata                        │
└─────────────────────────────────────┘
```

## File-to-Service Mapping

| File/Directory | Business Layer | Azure Service | Purpose |
|----------------|----------------|---------------|---------|
| `sap_simulator/` | Presentation | App Service | SAP simulation UI |
| `validation_service/` | API | Azure Functions | Validation API |
| `ai_agent.py` | Business Logic | Part of Functions | AI validation |
| `terraform/` | Infrastructure | N/A | IaC deployment |
| `create_sample_docs.py` | Testing | Local | Generate test data |

## Deployment Architecture

```
Customer Scenario (Production):
┌────────────┐
│    SAP     │ ──────┐
│  System    │       │
└────────────┘       │
                     ▼
                ┌─────────────────┐
                │  Azure Blob     │
                │   Storage       │
                └─────────────────┘
                     │
                     │ Blob Reference
                     ▼
                ┌─────────────────┐         ┌──────────────────┐
                │  Validation     │────────▶│  Azure Document  │
                │   Service       │         │  Intelligence    │
                │ (Azure Func)    │         └──────────────────┘
                └─────────────────┘
                     │
                     │ AI Analysis
                     ▼
                ┌─────────────────┐
                │  Azure OpenAI   │
                │    (GPT-4)      │
                └─────────────────┘
                     │
                     ▼
                 Validation Result


Demo Scenario (This Implementation):
┌────────────┐
│    SAP     │
│ Simulator  │ (Replaces real SAP)
│ (App Svc)  │
└────────────┘
     │
     │ Upload PDF
     ▼
┌─────────────────┐
│  Azure Blob     │
│   Storage       │
└─────────────────┘
     │
     │ API Call with Header
     ▼
┌─────────────────┐         ┌──────────────────┐
│  Validation     │────────▶│  Azure Document  │
│   Service       │         │  Intelligence    │
│ (Azure Func)    │         └──────────────────┘
└─────────────────┘
     │
     │ AI Validation
     ▼
┌─────────────────┐
│  AI Agent       │────────▶┌──────────────────┐
│   Module        │         │  Azure OpenAI    │
└─────────────────┘         │    (GPT-4)       │
                            └──────────────────┘
     │
     ▼
┌─────────────────┐
│    Result       │
│   Display       │
└─────────────────┘
```

## Cost Considerations

### Recommended for Demo/Testing:
- **SAP Simulator**: App Service B1 tier (~$13/month)
- **Validation Service**: Azure Functions Consumption Plan (pay-per-use, ~$0-5/month for demo)
- **Azure OpenAI**: Pay per token (~$0.03 per 1K tokens for GPT-4)
- **Document Intelligence**: Free tier (5,000 pages/month) or S0 tier
- **Blob Storage**: Standard LRS (~$0.018 per GB)

**Estimated Monthly Cost for Demo: $20-50**

### Recommended for Production:
- **Validation Service**: Azure Functions Premium Plan or App Service P1V2
- **Azure OpenAI**: Provisioned throughput for consistent performance
- **Document Intelligence**: S0 tier with scaling
- **Blob Storage**: Standard GRS for redundancy
- **Add**: Application Insights for monitoring
- **Add**: API Management for API governance

**Estimated Monthly Cost for Production: $200-500** (depends on volume)

## Recommended Deployment Strategy

### Option 1: Fully Serverless (Recommended for Demo)
```
SAP Simulator:     Azure App Service (B1)
Validation API:    Azure Functions (Consumption)
Document Intel:    Cognitive Services (Free/S0)
Storage:           Blob Storage (Standard)
AI:                Azure OpenAI (GPT-4)
```

### Option 2: Hybrid (Recommended for Production)
```
SAP Simulator:     Azure App Service (P1V2)
Validation API:    Azure Functions (Premium) + API Management
Document Intel:    Cognitive Services (S0 with autoscale)
Storage:           Blob Storage (GRS)
AI:                Azure OpenAI (Provisioned)
Monitoring:        Application Insights + Log Analytics
```

### Option 3: Container-Based (For Advanced Scenarios)
```
SAP Simulator:     Azure Container Apps
Validation API:    Azure Container Apps or AKS
Document Intel:    Cognitive Services
Storage:           Blob Storage
AI:                Azure OpenAI
Orchestration:     Azure Container Apps (with Dapr)
```

## Next Steps

1. **Deploy Infrastructure**: Run Terraform to create Azure resources
2. **Deploy SAP Simulator**: Deploy to App Service
3. **Deploy Validation Service**: Deploy to Azure Functions
4. **Configure AI**: Deploy GPT-4 model in Azure OpenAI
5. **Test**: Use sample documents to verify end-to-end flow
6. **Monitor**: Set up Application Insights

See `DEPLOYMENT.md` for detailed deployment instructions.
