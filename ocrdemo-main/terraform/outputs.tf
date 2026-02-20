output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.ocr_demo.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.ocr_storage.name
}

output "storage_account_url" {
  description = "Blob endpoint URL for the storage account"
  value       = azurerm_storage_account.ocr_storage.primary_blob_endpoint
}

output "blob_container_name" {
  description = "Name of the blob container"
  value       = azurerm_storage_container.delivery_documents.name
}

output "document_intelligence_endpoint" {
  description = "Endpoint for Document Intelligence"
  value       = azurerm_cognitive_account.document_intelligence.endpoint
}

output "openai_endpoint" {
  description = "Endpoint for Azure OpenAI"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "function_app_url" {
  description = "URL of the deployed Azure Function App"
  value       = "https://${azurerm_linux_function_app.validation_func.default_hostname}"
}

output "function_app_name" {
  description = "Name of the Function App"
  value       = azurerm_linux_function_app.validation_func.name
}

output "web_app_url" {
  description = "URL of the deployed SAP Simulator web app"
  value       = "https://${azurerm_linux_web_app.sap_simulator.default_hostname}"
}

output "web_app_name" {
  description = "Name of the SAP Simulator App Service"
  value       = azurerm_linux_web_app.sap_simulator.name
}

# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------
output "vnet_name" {
  description = "Name of the Virtual Network"
  value       = azurerm_virtual_network.main.name
}

output "vnet_id" {
  description = "Resource ID of the Virtual Network"
  value       = azurerm_virtual_network.main.id
}

# ---------------------------------------------------------------------------
# API Management
# ---------------------------------------------------------------------------
output "apim_gateway_url" {
  description = "APIM gateway URL – external consumers call this"
  value       = azurerm_api_management.apim.gateway_url
}

output "apim_name" {
  description = "Name of the APIM instance"
  value       = azurerm_api_management.apim.name
}

output "apim_subscription_key" {
  description = "APIM subscription primary key for SAP consumer"
  value       = azurerm_api_management_subscription.sap.primary_key
  sensitive   = true
}

# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------
output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  value       = azurerm_log_analytics_workspace.main.id
}

output "app_insights_connection_string" {
  description = "Application Insights connection string"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}
