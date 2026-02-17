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

# Resource Group
resource "azurerm_resource_group" "ocr_demo" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Storage Account for Blob Storage
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

# Blob Container for PDF documents
resource "azurerm_storage_container" "pdf_documents" {
  name                  = "discharge-documents"
  storage_account_name  = azurerm_storage_account.ocr_storage.name
  container_access_type = "private"
}

# Azure Cognitive Services - Document Intelligence (Form Recognizer)
resource "azurerm_cognitive_account" "document_intelligence" {
  name                = var.document_intelligence_name
  location            = azurerm_resource_group.ocr_demo.location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  kind                = "FormRecognizer"
  sku_name            = "S0"

  tags = var.tags
}

# Azure OpenAI for AI Agent (optional - for advanced AI capabilities)
resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_name
  location            = var.openai_location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  kind                = "OpenAI"
  sku_name            = "S0"

  tags = var.tags
}

# App Service Plan for hosting the Flask app
resource "azurerm_service_plan" "app_plan" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.ocr_demo.location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  os_type             = "Linux"
  sku_name            = "B1"

  tags = var.tags
}

# App Service for the Flask application
resource "azurerm_linux_web_app" "web_app" {
  name                = var.app_service_name
  location            = azurerm_resource_group.ocr_demo.location
  resource_group_name = azurerm_resource_group.ocr_demo.name
  service_plan_id     = azurerm_service_plan.app_plan.id

  site_config {
    always_on = false
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "AZURE_STORAGE_CONNECTION_STRING"     = azurerm_storage_account.ocr_storage.primary_connection_string
    "AZURE_STORAGE_CONTAINER_NAME"        = azurerm_storage_container.pdf_documents.name
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" = azurerm_cognitive_account.document_intelligence.endpoint
    "AZURE_DOCUMENT_INTELLIGENCE_KEY"     = azurerm_cognitive_account.document_intelligence.primary_access_key
    "AZURE_OPENAI_ENDPOINT"               = azurerm_cognitive_account.openai.endpoint
    "AZURE_OPENAI_KEY"                    = azurerm_cognitive_account.openai.primary_access_key
    "SCM_DO_BUILD_DURING_DEPLOYMENT"      = "true"
  }

  tags = var.tags
}
