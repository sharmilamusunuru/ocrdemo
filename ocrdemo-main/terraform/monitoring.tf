# ---------------------------------------------------------------------------
# Log Analytics Workspace
# ---------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_name
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

# ---------------------------------------------------------------------------
# Application Insights (workspace-based)
# ---------------------------------------------------------------------------
resource "azurerm_application_insights" "main" {
  name                = var.app_insights_name
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = var.tags
}

# ---------------------------------------------------------------------------
# Diagnostic Settings – API Management
# ---------------------------------------------------------------------------
resource "azurerm_monitor_diagnostic_setting" "apim" {
  name                       = "diag-apim"
  target_resource_id         = azurerm_api_management.apim.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "GatewayLogs"
  }

  metric {
    category = "AllMetrics"
  }
}

# ---------------------------------------------------------------------------
# Diagnostic Settings – Function App
# ---------------------------------------------------------------------------
resource "azurerm_monitor_diagnostic_setting" "func" {
  name                       = "diag-func"
  target_resource_id         = azurerm_linux_function_app.validation_func.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "FunctionAppLogs"
  }

  metric {
    category = "AllMetrics"
  }
}

# ---------------------------------------------------------------------------
# Diagnostic Settings – Web App (SAP Simulator)
# ---------------------------------------------------------------------------
resource "azurerm_monitor_diagnostic_setting" "webapp" {
  name                       = "diag-webapp"
  target_resource_id         = azurerm_linux_web_app.sap_simulator.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "AppServiceHTTPLogs"
  }

  enabled_log {
    category = "AppServiceConsoleLogs"
  }

  metric {
    category = "AllMetrics"
  }
}
