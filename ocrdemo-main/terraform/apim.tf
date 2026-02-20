# ---------------------------------------------------------------------------
# Azure API Management – Gateway for external SAP consumers
# ---------------------------------------------------------------------------
resource "azurerm_api_management" "apim" {
  name                = var.apim_name
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  publisher_name      = var.apim_publisher_name
  publisher_email     = var.apim_publisher_email
  sku_name            = "Basicv2_1"
  tags                = var.tags
}

# ---------------------------------------------------------------------------
# Named Value – Function App host key (secret, injected by APIM policy)
# ---------------------------------------------------------------------------
resource "azurerm_api_management_named_value" "func_key" {
  name                = "function-app-key"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  api_management_name = azurerm_api_management.apim.name
  display_name        = "function-app-key"
  value               = data.azurerm_function_app_host_keys.validation_func.default_function_key
  secret              = true
}

# ---------------------------------------------------------------------------
# API Definition – Delivery Validation
# ---------------------------------------------------------------------------
resource "azurerm_api_management_api" "validation" {
  name                  = "delivery-validation-api"
  resource_group_name   = azurerm_resource_group.ocr_demo.name
  api_management_name   = azurerm_api_management.apim.name
  revision              = "1"
  display_name          = "Delivery Validation API"
  description           = "Validates delivery quantities against shipping documents using OCR and AI"
  path                  = "api"
  protocols             = ["https"]
  service_url           = "https://${azurerm_linux_function_app.validation_func.default_hostname}/api"
  subscription_required = true
}

# ---------------------------------------------------------------------------
# API Operations
# ---------------------------------------------------------------------------
resource "azurerm_api_management_api_operation" "validate" {
  operation_id        = "validate-delivery"
  api_name            = azurerm_api_management_api.validation.name
  api_management_name = azurerm_api_management.apim.name
  resource_group_name = azurerm_resource_group.ocr_demo.name
  display_name        = "Validate Delivery Quantity"
  method              = "POST"
  url_template        = "/validate"
  description         = "Validate a delivery quantity against the uploaded PDF document"

  request {
    description = "Validation request with record_id, delivery_quantity, and blob_name"

    representation {
      content_type = "application/json"
      example {
        name  = "ValidateRequest"
        value = jsonencode({
          record_id         = "20260220-ABC12345"
          delivery_quantity  = 1234.56
          blob_name         = "20260220-ABC12345/raw/document.pdf"
        })
      }
    }
  }

  response {
    status_code = 200
    description = "Validation result"

    representation {
      content_type = "application/json"
    }
  }

  response {
    status_code = 400
    description = "Bad request – missing or invalid fields"
  }

  response {
    status_code = 500
    description = "Internal server error"
  }
}

resource "azurerm_api_management_api_operation" "health" {
  operation_id        = "health-check"
  api_name            = azurerm_api_management_api.validation.name
  api_management_name = azurerm_api_management.apim.name
  resource_group_name = azurerm_resource_group.ocr_demo.name
  display_name        = "Health Check"
  method              = "GET"
  url_template        = "/health"
  description         = "Check service health status"

  response {
    status_code = 200
    description = "Service is healthy"
  }
}

# ---------------------------------------------------------------------------
# API Policy – rate limiting, function key injection, correlation ID
# ---------------------------------------------------------------------------
resource "azurerm_api_management_api_policy" "validation" {
  api_name            = azurerm_api_management_api.validation.name
  api_management_name = azurerm_api_management.apim.name
  resource_group_name = azurerm_resource_group.ocr_demo.name

  xml_content = <<-XML
    <policies>
      <inbound>
        <base />
        <!-- Rate limiting: 100 calls per 60 seconds per subscription -->
        <rate-limit calls="100" renewal-period="60" />
        <!-- Inject Function App host key for backend authentication -->
        <set-header name="x-functions-key" exists-action="override">
          <value>{{function-app-key}}</value>
        </set-header>
        <!-- Propagate or generate a correlation ID -->
        <set-header name="X-Correlation-ID" exists-action="skip">
          <value>@(context.RequestId)</value>
        </set-header>
      </inbound>
      <backend>
        <base />
      </backend>
      <outbound>
        <base />
        <!-- Strip internal headers from the response -->
        <set-header name="X-Powered-By" exists-action="delete" />
        <set-header name="X-AspNet-Version" exists-action="delete" />
      </outbound>
      <on-error>
        <base />
        <return-response>
          <set-status code="500" reason="Internal Server Error" />
          <set-header name="Content-Type" exists-action="override">
            <value>application/json</value>
          </set-header>
          <set-body>{"status": "error", "remarks": "An error occurred processing your request. Please try again later."}</set-body>
        </return-response>
      </on-error>
    </policies>
  XML
}

# ---------------------------------------------------------------------------
# APIM Subscription – for SAP / external consumers
# ---------------------------------------------------------------------------
resource "azurerm_api_management_subscription" "sap" {
  resource_group_name = azurerm_resource_group.ocr_demo.name
  api_management_name = azurerm_api_management.apim.name
  display_name        = "SAP-Consumer"
  api_id              = azurerm_api_management_api.validation.id
  state               = "active"
}
