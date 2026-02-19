terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# ---------------------------------------------------------------------------
# Resource Group
# ---------------------------------------------------------------------------
resource "azurerm_resource_group" "ocr_demo" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# ---------------------------------------------------------------------------
# Storage Account – holds delivery-documents container
#   /{record_id}/raw/       – raw PDF uploaded by SAP
#   /{record_id}/processed/ – JSON validation result
# ---------------------------------------------------------------------------
resource "azurerm_storage_account" "ocr_storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.ocr_demo.name
  location                 = azurerm_resource_group.ocr_demo.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  blob_properties {
    cors_rule {
      allowed_headers    = ["*"]
      allowed_methods    = ["GET", "POST", "PUT"]
      allowed_origins    = ["*"]
      exposed_headers    = ["*"]
      max_age_in_seconds = 3600
    }
  }

  tags = var.tags
}

resource "azurerm_storage_container" "delivery_documents" {
  name                  = "delivery-documents"
  storage_account_name  = azurerm_storage_account.ocr_storage.name
  container_access_type = "private"
}

# ---------------------------------------------------------------------------
# Azure Document Intelligence (Form Recognizer) – OCR / text extraction
# ---------------------------------------------------------------------------
resource "azurerm_cognitive_account" "document_intelligence" {
  name                = var.document_intelligence_name
  location            = azurerm_resource_group.ocr_demo.location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  kind                = "FormRecognizer"
  sku_name            = "S0"
  tags                = var.tags
}

# ---------------------------------------------------------------------------
# Azure OpenAI – AI agent for smart quantity matching (optional)
# ---------------------------------------------------------------------------
resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_name
  location            = var.openai_location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  kind                = "OpenAI"
  sku_name            = "S0"
  tags                = var.tags
}

# GPT-4o model deployment inside the OpenAI account
resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-08-06"
  }

  sku {
    name     = "Standard"
    capacity = 10
  }
}

# ---------------------------------------------------------------------------
# Azure Functions – validation API
# ---------------------------------------------------------------------------

# Dedicated storage account for the Functions runtime
resource "azurerm_storage_account" "func_storage" {
  name                     = var.function_storage_account_name
  resource_group_name      = azurerm_resource_group.ocr_demo.name
  location                 = azurerm_resource_group.ocr_demo.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

# Shared Linux B1 plan for both Function App and Web App
resource "azurerm_service_plan" "shared_plan" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.ocr_demo.location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  os_type             = "Linux"
  sku_name            = "B1"
  tags                = var.tags
}

# Function App – Python 3.11
resource "azurerm_linux_function_app" "validation_func" {
  name                = var.function_app_name
  location            = azurerm_resource_group.ocr_demo.location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  service_plan_id     = azurerm_service_plan.shared_plan.id

  storage_account_name       = azurerm_storage_account.func_storage.name
  storage_account_access_key = azurerm_storage_account.func_storage.primary_access_key

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    # Data storage (delivery-documents container)
    "AZURE_STORAGE_CONNECTION_STRING"      = azurerm_storage_account.ocr_storage.primary_connection_string
    "AZURE_STORAGE_CONTAINER_NAME"         = azurerm_storage_container.delivery_documents.name

    # Document Intelligence
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" = azurerm_cognitive_account.document_intelligence.endpoint
    "AZURE_DOCUMENT_INTELLIGENCE_KEY"      = azurerm_cognitive_account.document_intelligence.primary_access_key

    # Azure OpenAI (AI agent)
    "AZURE_OPENAI_ENDPOINT"                = azurerm_cognitive_account.openai.endpoint
    "AZURE_OPENAI_KEY"                     = azurerm_cognitive_account.openai.primary_access_key
    "AZURE_OPENAI_DEPLOYMENT"              = "gpt-4o"

    # Functions runtime
    "FUNCTIONS_WORKER_RUNTIME"             = "python"
    "SCM_DO_BUILD_DURING_DEPLOYMENT"       = "true"
    "BUILD_FLAGS"                          = "UseExpressBuild"
    "ENABLE_ORYX_BUILD"                    = "true"
  }

  tags = var.tags
}

# ---------------------------------------------------------------------------
# Azure App Service – SAP Simulator (Flask front-end)
# ---------------------------------------------------------------------------

# App Service – Python 3.11 (shares the B1 plan with Function App)
resource "azurerm_linux_web_app" "sap_simulator" {
  name                = var.app_service_name
  location            = azurerm_resource_group.ocr_demo.location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  service_plan_id     = azurerm_service_plan.shared_plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
    app_command_line = "gunicorn --bind=0.0.0.0 --timeout 300 app:app"
  }

  app_settings = {
    # Azure Blob Storage (shared with validation service)
    "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.ocr_storage.primary_connection_string
    "AZURE_STORAGE_CONTAINER_NAME"    = azurerm_storage_container.delivery_documents.name

    # Validation Function URL
    "VALIDATION_SERVICE_URL"          = "https://${azurerm_linux_function_app.validation_func.default_hostname}"

    # Azure OpenAI (AI agent for SAP-side validation)
    "AZURE_OPENAI_ENDPOINT"           = azurerm_cognitive_account.openai.endpoint
    "AZURE_OPENAI_KEY"                = azurerm_cognitive_account.openai.primary_access_key
    "AZURE_OPENAI_DEPLOYMENT"         = "gpt-4o"

    # Build settings
    "SCM_DO_BUILD_DURING_DEPLOYMENT"  = "true"
  }

  tags = var.tags
}
