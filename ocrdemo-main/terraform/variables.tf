variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "rg-ocr-demo-bhp"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "australiaeast"
}

variable "openai_location" {
  description = "Azure region for OpenAI (limited availability)"
  type        = string
  default     = "australiaeast"
}

variable "storage_account_name" {
  description = "Name of the Azure Storage Account (must be globally unique)"
  type        = string
  default     = "stocrbhpdemo2026"
  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 characters, lowercase letters and numbers only."
  }
}

variable "document_intelligence_name" {
  description = "Name of the Document Intelligence resource"
  type        = string
  default     = "di-ocr-bhp-2026"
}

variable "openai_name" {
  description = "Name of the Azure OpenAI resource"
  type        = string
  default     = "oai-ocr-bhp-2026"
}

variable "function_storage_account_name" {
  description = "Name of the Storage Account for Azure Functions runtime (must be globally unique)"
  type        = string
  default     = "stocrbhpfa2026"
  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.function_storage_account_name))
    error_message = "Storage account name must be 3-24 characters, lowercase letters and numbers only."
  }
}

variable "function_plan_name" {
  description = "Name of the Function App Consumption Plan"
  type        = string
  default     = "plan-ocr-bhp-func"
}

variable "function_app_name" {
  description = "Name of the Azure Function App (must be globally unique)"
  type        = string
  default     = "func-ocr-bhp-2026"
}

variable "app_service_plan_name" {
  description = "Name of the App Service Plan for the SAP Simulator"
  type        = string
  default     = "plan-ocr-bhp-web"
}

variable "app_service_name" {
  description = "Name of the App Service for the SAP Simulator (must be globally unique)"
  type        = string
  default     = "app-ocr-bhp-2026"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "Demo"
    Project     = "OCR-Validation"
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------
variable "vnet_name" {
  description = "Name of the Virtual Network"
  type        = string
  default     = "vnet-ocr-bhp-2026"
}

# ---------------------------------------------------------------------------
# API Management
# ---------------------------------------------------------------------------
variable "apim_name" {
  description = "Name of the Azure API Management instance (must be globally unique)"
  type        = string
  default     = "apim-ocr-bhp-2026"
}

variable "apim_publisher_name" {
  description = "Publisher name shown in the APIM developer portal"
  type        = string
  default     = "OCR Demo BHP"
}

variable "apim_publisher_email" {
  description = "Publisher email for APIM notifications"
  type        = string
  default     = "admin@ocr-demo-bhp.com"
}

# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------
variable "log_analytics_name" {
  description = "Name of the Log Analytics Workspace"
  type        = string
  default     = "law-ocr-bhp-2026"
}

variable "app_insights_name" {
  description = "Name of the Application Insights resource"
  type        = string
  default     = "appi-ocr-bhp-2026"
}
