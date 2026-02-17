variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "rg-ocr-demo"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "openai_location" {
  description = "Azure region for OpenAI (limited availability)"
  type        = string
  default     = "eastus"
}

variable "storage_account_name" {
  description = "Name of the Azure Storage Account (must be globally unique)"
  type        = string
  default     = "stocrdemo"
  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account name must be 3-24 characters, lowercase letters and numbers only."
  }
}

variable "document_intelligence_name" {
  description = "Name of the Document Intelligence resource"
  type        = string
  default     = "di-ocr-demo"
}

variable "openai_name" {
  description = "Name of the Azure OpenAI resource"
  type        = string
  default     = "oai-ocr-demo"
}

variable "app_service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
  default     = "asp-ocr-demo"
}

variable "app_service_name" {
  description = "Name of the App Service (must be globally unique)"
  type        = string
  default     = "app-ocr-demo"
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
