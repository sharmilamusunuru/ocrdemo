# Terraform Infrastructure

This directory contains Infrastructure as Code (IaC) for deploying the OCR Demo solution to Azure.

## Resources Created

- **Resource Group**: Container for all resources
- **Storage Account**: Azure Blob Storage for PDF documents
- **Blob Container**: `discharge-documents` container
- **Azure Document Intelligence**: OCR and document analysis service
- **Azure OpenAI**: GPT-4 for AI-powered validation
- **App Service Plan**: Linux-based hosting plan
- **App Service**: For hosting the SAP Simulator web app

## Usage

### Initialize
```bash
terraform init
```

### Plan
```bash
terraform plan -out=tfplan
```

### Apply
```bash
terraform apply tfplan
```

### Destroy
```bash
terraform destroy
```

## Variables

Key variables that should be customized:

- `storage_account_name`: Must be globally unique (3-24 lowercase letters/numbers)
- `app_service_name`: Must be globally unique
- `location`: Azure region (default: eastus)
- `openai_location`: OpenAI region (limited availability)

Create a `terraform.tfvars` file with your custom values:

```hcl
storage_account_name = "stocrdemo12345"
app_service_name     = "app-ocr-demo-unique"
location            = "eastus"
```

## Outputs

After deployment, the following outputs are available:

- `web_app_url`: URL of the deployed SAP Simulator
- `storage_connection_string`: Connection string for blob storage (sensitive)
- `document_intelligence_endpoint`: Document Intelligence API endpoint
- `document_intelligence_key`: API key (sensitive)
- `openai_endpoint`: Azure OpenAI endpoint
- `openai_key`: Azure OpenAI key (sensitive)

View outputs:
```bash
terraform output
terraform output -raw web_app_url
terraform output -json > outputs.json
```

## State Management

**Local State** (default):
- State file stored locally as `terraform.tfstate`
- Not recommended for team environments

**Remote State** (recommended for production):
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "sttfstate"
    container_name       = "tfstate"
    key                  = "ocrdemo.terraform.tfstate"
  }
}
```

## Security Notes

- Never commit `terraform.tfstate` or sensitive outputs to Git
- Use Azure Key Vault for production secrets
- Enable Managed Identity instead of connection strings where possible
- Review and adjust firewall rules before production deployment
