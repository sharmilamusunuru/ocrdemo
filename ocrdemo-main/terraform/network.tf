# ---------------------------------------------------------------------------
# Virtual Network & Subnets
# ---------------------------------------------------------------------------
resource "azurerm_virtual_network" "main" {
  name                = var.vnet_name
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  address_space       = ["10.0.0.0/16"]
  tags                = var.tags
}

# Subnet for Azure Function App – outbound VNet integration
resource "azurerm_subnet" "func_integration" {
  name                 = "snet-func-integration"
  resource_group_name  = azurerm_resource_group.ocr_demo.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]

  delegation {
    name = "func-delegation"
    service_delegation {
      name    = "Microsoft.Web/serverFarms"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

# Subnet for Web App (SAP Simulator) – outbound VNet integration
resource "azurerm_subnet" "webapp_integration" {
  name                 = "snet-webapp-integration"
  resource_group_name  = azurerm_resource_group.ocr_demo.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]

  delegation {
    name = "webapp-delegation"
    service_delegation {
      name    = "Microsoft.Web/serverFarms"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

# Subnet for Private Endpoints
resource "azurerm_subnet" "private_endpoints" {
  name                 = "snet-private-endpoints"
  resource_group_name  = azurerm_resource_group.ocr_demo.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.3.0/24"]
}

# ---------------------------------------------------------------------------
# Network Security Groups
# ---------------------------------------------------------------------------
resource "azurerm_network_security_group" "private_endpoints" {
  name                = "nsg-private-endpoints"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  tags                = var.tags
}

resource "azurerm_subnet_network_security_group_association" "private_endpoints" {
  subnet_id                 = azurerm_subnet.private_endpoints.id
  network_security_group_id = azurerm_network_security_group.private_endpoints.id
}

# ---------------------------------------------------------------------------
# Private DNS Zones
# ---------------------------------------------------------------------------
resource "azurerm_private_dns_zone" "blob" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  tags                = var.tags
}

resource "azurerm_private_dns_zone" "table" {
  name                = "privatelink.table.core.windows.net"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  tags                = var.tags
}

resource "azurerm_private_dns_zone" "queue" {
  name                = "privatelink.queue.core.windows.net"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  tags                = var.tags
}

resource "azurerm_private_dns_zone" "file" {
  name                = "privatelink.file.core.windows.net"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  tags                = var.tags
}

resource "azurerm_private_dns_zone" "cognitive" {
  name                = "privatelink.cognitiveservices.azure.com"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  tags                = var.tags
}

resource "azurerm_private_dns_zone" "openai" {
  name                = "privatelink.openai.azure.com"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  tags                = var.tags
}

# ---------------------------------------------------------------------------
# Private DNS Zone → VNet Links
# ---------------------------------------------------------------------------
resource "azurerm_private_dns_zone_virtual_network_link" "blob" {
  name                  = "link-blob"
  resource_group_name   = azurerm_resource_group.ocr_demo.name
  private_dns_zone_name = azurerm_private_dns_zone.blob.name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = false
  tags                  = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "table" {
  name                  = "link-table"
  resource_group_name   = azurerm_resource_group.ocr_demo.name
  private_dns_zone_name = azurerm_private_dns_zone.table.name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = false
  tags                  = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "queue" {
  name                  = "link-queue"
  resource_group_name   = azurerm_resource_group.ocr_demo.name
  private_dns_zone_name = azurerm_private_dns_zone.queue.name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = false
  tags                  = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "file" {
  name                  = "link-file"
  resource_group_name   = azurerm_resource_group.ocr_demo.name
  private_dns_zone_name = azurerm_private_dns_zone.file.name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = false
  tags                  = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "cognitive" {
  name                  = "link-cognitive"
  resource_group_name   = azurerm_resource_group.ocr_demo.name
  private_dns_zone_name = azurerm_private_dns_zone.cognitive.name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = false
  tags                  = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "openai" {
  name                  = "link-openai"
  resource_group_name   = azurerm_resource_group.ocr_demo.name
  private_dns_zone_name = azurerm_private_dns_zone.openai.name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = false
  tags                  = var.tags
}

# ---------------------------------------------------------------------------
# Private Endpoints – Data Storage Account (blob)
# ---------------------------------------------------------------------------
resource "azurerm_private_endpoint" "ocr_storage_blob" {
  name                = "pe-${var.storage_account_name}-blob"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "psc-${var.storage_account_name}-blob"
    private_connection_resource_id = azurerm_storage_account.ocr_storage.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-blob"
    private_dns_zone_ids = [azurerm_private_dns_zone.blob.id]
  }
}

# ---------------------------------------------------------------------------
# Private Endpoints – Functions Runtime Storage (blob, table, queue, file)
# ---------------------------------------------------------------------------
resource "azurerm_private_endpoint" "func_storage_blob" {
  name                = "pe-${var.function_storage_account_name}-blob"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "psc-${var.function_storage_account_name}-blob"
    private_connection_resource_id = azurerm_storage_account.func_storage.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-blob"
    private_dns_zone_ids = [azurerm_private_dns_zone.blob.id]
  }
}

resource "azurerm_private_endpoint" "func_storage_table" {
  name                = "pe-${var.function_storage_account_name}-table"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "psc-${var.function_storage_account_name}-table"
    private_connection_resource_id = azurerm_storage_account.func_storage.id
    subresource_names              = ["table"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-table"
    private_dns_zone_ids = [azurerm_private_dns_zone.table.id]
  }
}

resource "azurerm_private_endpoint" "func_storage_queue" {
  name                = "pe-${var.function_storage_account_name}-queue"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "psc-${var.function_storage_account_name}-queue"
    private_connection_resource_id = azurerm_storage_account.func_storage.id
    subresource_names              = ["queue"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-queue"
    private_dns_zone_ids = [azurerm_private_dns_zone.queue.id]
  }
}

resource "azurerm_private_endpoint" "func_storage_file" {
  name                = "pe-${var.function_storage_account_name}-file"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "psc-${var.function_storage_account_name}-file"
    private_connection_resource_id = azurerm_storage_account.func_storage.id
    subresource_names              = ["file"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-file"
    private_dns_zone_ids = [azurerm_private_dns_zone.file.id]
  }
}

# ---------------------------------------------------------------------------
# Private Endpoints – Azure Document Intelligence
# ---------------------------------------------------------------------------
resource "azurerm_private_endpoint" "document_intelligence" {
  name                = "pe-${var.document_intelligence_name}"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "psc-${var.document_intelligence_name}"
    private_connection_resource_id = azurerm_cognitive_account.document_intelligence.id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-cognitive"
    private_dns_zone_ids = [azurerm_private_dns_zone.cognitive.id]
  }
}

# ---------------------------------------------------------------------------
# Private Endpoints – Azure OpenAI
# ---------------------------------------------------------------------------
resource "azurerm_private_endpoint" "openai" {
  name                = "pe-${var.openai_name}"
  resource_group_name = azurerm_resource_group.ocr_demo.name
  location            = azurerm_resource_group.ocr_demo.location
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = var.tags

  private_service_connection {
    name                           = "psc-${var.openai_name}"
    private_connection_resource_id = azurerm_cognitive_account.openai.id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-openai"
    private_dns_zone_ids = [azurerm_private_dns_zone.openai.id]
  }
}

# ---------------------------------------------------------------------------
# Storage Account Network Rules – deny public, allow VNet + Azure Services
# (separate resources to ensure private endpoints + containers exist first)
# ---------------------------------------------------------------------------
resource "azurerm_storage_account_network_rules" "ocr_storage" {
  storage_account_id = azurerm_storage_account.ocr_storage.id
  default_action     = "Deny"
  bypass             = ["AzureServices"]

  depends_on = [
    azurerm_storage_container.delivery_documents,
    azurerm_private_endpoint.ocr_storage_blob,
    azurerm_subnet.func_integration,
    azurerm_subnet.webapp_integration,
  ]
}

resource "azurerm_storage_account_network_rules" "func_storage" {
  storage_account_id = azurerm_storage_account.func_storage.id
  default_action     = "Deny"
  bypass             = ["AzureServices"]

  depends_on = [
    azurerm_private_endpoint.func_storage_blob,
    azurerm_private_endpoint.func_storage_table,
    azurerm_private_endpoint.func_storage_queue,
    azurerm_private_endpoint.func_storage_file,
    azurerm_subnet.func_integration,
  ]
}
