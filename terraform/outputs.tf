output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.ocr_demo.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.ocr_storage.name
}

output "storage_connection_string" {
  description = "Connection string for storage account"
  value       = azurerm_storage_account.ocr_storage.primary_connection_string
  sensitive   = true
}

output "blob_container_name" {
  description = "Name of the blob container"
  value       = azurerm_storage_container.pdf_documents.name
}

output "document_intelligence_endpoint" {
  description = "Endpoint for Document Intelligence"
  value       = azurerm_cognitive_account.document_intelligence.endpoint
}

output "document_intelligence_key" {
  description = "Primary key for Document Intelligence"
  value       = azurerm_cognitive_account.document_intelligence.primary_access_key
  sensitive   = true
}

output "openai_endpoint" {
  description = "Endpoint for Azure OpenAI"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "openai_key" {
  description = "Primary key for Azure OpenAI"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "web_app_url" {
  description = "URL of the deployed web application"
  value       = "https://${azurerm_linux_web_app.web_app.default_hostname}"
}

output "web_app_name" {
  description = "Name of the web app"
  value       = azurerm_linux_web_app.web_app.name
}
