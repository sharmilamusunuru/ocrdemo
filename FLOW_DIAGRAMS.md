# System Flow Diagrams

## Overview
This document contains detailed flow diagrams showing how the system works from user interaction to validation result.

## 1. High-Level Process Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 1: User uploads PDF and enters discharge quantity             │
│  Location: SAP Simulator Web UI                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 2: SAP Simulator uploads PDF to Azure Blob Storage            │
│  Service: Azure Blob Storage API                                    │
│  Output: blob_name, blob_url                                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 3: SAP Simulator calls Validation Service API                 │
│  Method: POST /api/validate                                         │
│  Header: X-Discharge-Quantity: <entered_value>                      │
│  Body: { "blob_name": "<blob_reference>" }                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 4: Validation Service retrieves PDF from Blob Storage         │
│  Service: Azure Blob Storage                                        │
│  Output: blob_url for Document Intelligence                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 5: Document Intelligence extracts text from PDF               │
│  Service: Azure Document Intelligence                               │
│  Model: prebuilt-document                                           │
│  Output: extracted_text, document_structure                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 6: Extract numerical quantities using regex                   │
│  Location: Validation Service (Python)                              │
│  Output: List of numbers found in document                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 7: AI Agent analyzes and validates                            │
│  Service: Azure OpenAI (GPT-4)                                      │
│  Input: extracted_text, entered_quantity, found_quantities          │
│  Output: is_valid, confidence, reasoning, matched_value             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 8: Return validation result to SAP Simulator                  │
│  Response: JSON with validation details                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Step 9: Display result in UI (Success/Failure)                     │
│  Location: SAP Simulator Web UI                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Detailed Sequence Diagram

```
User          SAP Simulator    Blob Storage    Validation API    Doc Intelligence    AI Agent
 │                 │                │                │                  │               │
 │ Upload PDF      │                │                │                  │               │
 │ Enter Quantity  │                │                │                  │               │
 │────────────────>│                │                │                  │               │
 │                 │                │                │                  │               │
 │                 │ Upload File    │                │                  │               │
 │                 │───────────────>│                │                  │               │
 │                 │                │                │                  │               │
 │                 │   blob_name    │                │                  │               │
 │                 │<───────────────│                │                  │               │
 │                 │                │                │                  │               │
 │                 │ POST /api/validate              │                  │               │
 │                 │ X-Discharge-Quantity: 1234.56   │                  │               │
 │                 │ {"blob_name": "xyz.pdf"}        │                  │               │
 │                 │────────────────────────────────>│                  │               │
 │                 │                │                │                  │               │
 │                 │                │                │ Get blob URL     │               │
 │                 │                │<───────────────│                  │               │
 │                 │                │                │                  │               │
 │                 │                │                │ Analyze Document │               │
 │                 │                │                │─────────────────>│               │
 │                 │                │                │                  │               │
 │                 │                │                │  Extracted Text  │               │
 │                 │                │                │<─────────────────│               │
 │                 │                │                │                  │               │
 │                 │                │                │ Extract Numbers  │               │
 │                 │                │                │ (Regex)          │               │
 │                 │                │                │                  │               │
 │                 │                │                │ Validate with AI │               │
 │                 │                │                │─────────────────────────────────>│
 │                 │                │                │                  │               │
 │                 │                │                │                  │  Call GPT-4   │
 │                 │                │                │                  │  Analyze      │
 │                 │                │                │                  │               │
 │                 │                │                │     Validation   │               │
 │                 │                │                │     Result       │               │
 │                 │                │                │<─────────────────────────────────│
 │                 │                │                │                  │               │
 │                 │   Validation Response            │                  │               │
 │                 │<────────────────────────────────│                  │               │
 │                 │                │                │                  │               │
 │  Display Result │                │                │                  │               │
 │<────────────────│                │                │                  │               │
 │                 │                │                │                  │               │
```

## 3. Data Flow Diagram

```
┌──────────────┐
│   User       │
│   Input      │
└──────────────┘
       │
       │ PDF File + Quantity
       ▼
┌──────────────────────────────────┐
│   SAP Simulator (App Service)    │
│                                  │
│   Data Created:                  │
│   - File content (binary)        │
│   - Quantity value (float)       │
│   - Filename (string)            │
└──────────────────────────────────┘
       │
       │ HTTP POST (multipart/form-data)
       ▼
┌──────────────────────────────────┐
│   Azure Blob Storage             │
│                                  │
│   Data Stored:                   │
│   - PDF file (blob)              │
│   - Blob name (reference)        │
│   - Blob URL                     │
└──────────────────────────────────┘
       │
       │ blob_name passed to API
       ▼
┌──────────────────────────────────┐
│   Validation Service             │
│   (Azure Functions)              │
│                                  │
│   Receives:                      │
│   - X-Discharge-Quantity header  │
│   - blob_name in JSON body       │
└──────────────────────────────────┘
       │
       │ blob_url retrieved
       ▼
┌──────────────────────────────────┐
│   Azure Document Intelligence    │
│                                  │
│   Processes:                     │
│   - PDF layout analysis          │
│   - OCR text extraction          │
│                                  │
│   Returns:                       │
│   - Full text content            │
│   - Document structure           │
│   - Page information             │
└──────────────────────────────────┘
       │
       │ extracted_text
       ▼
┌──────────────────────────────────┐
│   Regex Parser                   │
│                                  │
│   Extracts:                      │
│   - All numeric values           │
│   - Formats: 123, 123.45, etc.   │
│                                  │
│   Output: [2024, 1, 17, 1234.56] │
└──────────────────────────────────┘
       │
       │ text + quantities + entered_value
       ▼
┌──────────────────────────────────┐
│   AI Agent Module                │
│                                  │
│   Creates prompt with:           │
│   - Document text                │
│   - Extracted quantities         │
│   - User entered quantity        │
└──────────────────────────────────┘
       │
       │ GPT-4 API call
       ▼
┌──────────────────────────────────┐
│   Azure OpenAI (GPT-4)           │
│                                  │
│   Analyzes:                      │
│   - Context of numbers           │
│   - Discharge quantity field     │
│   - Formatting variations        │
│                                  │
│   Returns:                       │
│   - is_valid (boolean)           │
│   - matched_value (float)        │
│   - confidence (0-100)           │
│   - reasoning (string)           │
└──────────────────────────────────┘
       │
       │ Validation result
       ▼
┌──────────────────────────────────┐
│   Response Assembly              │
│                                  │
│   Combines:                      │
│   - Simple validation result     │
│   - AI validation result         │
│   - Metadata                     │
│                                  │
│   JSON Response                  │
└──────────────────────────────────┘
       │
       │ HTTP Response
       ▼
┌──────────────────────────────────┐
│   SAP Simulator UI               │
│                                  │
│   Displays:                      │
│   - Success/Failure status       │
│   - Matched quantity             │
│   - AI confidence                │
│   - All extracted values         │
└──────────────────────────────────┘
```

## 4. Component Interaction Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND TIER                            │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  SAP Simulator Web Application                       │       │
│  │  - File upload component                             │       │
│  │  - Quantity input field                              │       │
│  │  - Result display component                          │       │
│  │                                                       │       │
│  │  Technology: Flask + HTML/CSS/JavaScript             │       │
│  │  Azure Service: App Service (B1)                     │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API TIER                                 │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Validation Service REST API                         │       │
│  │  - /api/validate endpoint                            │       │
│  │  - /api/analyze-structure endpoint                   │       │
│  │  - /health endpoint                                  │       │
│  │                                                       │       │
│  │  Technology: Flask REST API                          │       │
│  │  Azure Service: Azure Functions (Consumption)        │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│    BUSINESS LOGIC TIER   │  │     AI SERVICES TIER     │
│                          │  │                          │
│  ┌────────────────────┐  │  │  ┌────────────────────┐  │
│  │  AI Agent Module   │  │  │  │  Azure OpenAI      │  │
│  │  - validate()      │──┼──┼─>│  - GPT-4 Model     │  │
│  │  - analyze_doc()   │  │  │  │  - JSON responses  │  │
│  │                    │  │  │  └────────────────────┘  │
│  │  Technology: Python│  │  │                          │
│  │  Integrated in API │  │  │  ┌────────────────────┐  │
│  └────────────────────┘  │  │  │  Azure Document    │  │
│                          │  │  │  Intelligence      │  │
│  ┌────────────────────┐  │  │  │  - OCR Engine      │  │
│  │  Quantity Extractor│<─┼──┼──│  - Layout Analysis │  │
│  │  - Regex patterns  │  │  │  └────────────────────┘  │
│  │  - Number parsing  │  │  │                          │
│  └────────────────────┘  │  └──────────────────────────┘
└──────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATA TIER                                │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Azure Blob Storage                                  │       │
│  │  Container: discharge-documents                      │       │
│  │  - PDF files                                         │       │
│  │  - Metadata (timestamps, filenames)                  │       │
│  │                                                       │       │
│  │  Technology: Azure Storage SDK                       │       │
│  │  Redundancy: LRS (configurable to GRS)              │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 5. Deployment Flow

```
Developer        CI/CD Pipeline      Azure Resources      Application
    │                  │                    │                  │
    │  git push        │                    │                  │
    │─────────────────>│                    │                  │
    │                  │                    │                  │
    │                  │ terraform apply    │                  │
    │                  │───────────────────>│                  │
    │                  │                    │                  │
    │                  │    Resources       │                  │
    │                  │    Created         │                  │
    │                  │<───────────────────│                  │
    │                  │                    │                  │
    │                  │ Deploy SAP Sim     │                  │
    │                  │───────────────────────────────────────>│
    │                  │                    │                  │
    │                  │ Deploy Validation  │                  │
    │                  │    Service         │                  │
    │                  │───────────────────────────────────────>│
    │                  │                    │                  │
    │                  │ Configure          │                  │
    │                  │ Environment Vars   │                  │
    │                  │───────────────────────────────────────>│
    │                  │                    │                  │
    │                  │     Application    │                  │
    │                  │     Running        │                  │
    │                  │<───────────────────────────────────────│
    │                  │                    │                  │
    │  Access URL      │                    │                  │
    │<─────────────────│                    │                  │
```

## 6. Error Handling Flow

```
Request
   │
   ▼
┌─────────────────────┐
│ Input Validation    │
│ - File type check   │
│ - Quantity format   │
└─────────────────────┘
   │
   │ Valid?
   ├─No──> Return 400 Error
   │
   ▼ Yes
┌─────────────────────┐
│ Blob Upload         │
└─────────────────────┘
   │
   │ Success?
   ├─No──> Return 500 Error (Storage)
   │
   ▼ Yes
┌─────────────────────┐
│ API Call            │
└─────────────────────┘
   │
   │ Reachable?
   ├─No──> Return 503 Error (Service Unavailable)
   │
   ▼ Yes
┌─────────────────────┐
│ Document Analysis   │
└─────────────────────┘
   │
   │ Success?
   ├─No──> Fallback: Manual validation
   │
   ▼ Yes
┌─────────────────────┐
│ AI Validation       │
└─────────────────────┘
   │
   │ Available?
   ├─No──> Use simple regex validation
   │
   ▼ Yes
┌─────────────────────┐
│ Return Result       │
└─────────────────────┘
```

## Key Points

1. **Separation of Concerns**: SAP Simulator and Validation Service are independent
2. **Stateless Design**: Each request is independent, perfect for Functions
3. **Scalability**: All components can scale independently
4. **Resilience**: Fallback mechanisms if AI services unavailable
5. **Monitoring**: All components support Application Insights integration
