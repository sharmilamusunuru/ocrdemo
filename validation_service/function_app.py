"""
Azure Validation Service – Azure Functions (v2 Python model)

Flow triggered by SAP (or the SAP Simulator):
1. SAP uploads PDF to  delivery-documents/{record_id}/raw/{filename}
2. SAP calls POST /api/validate with JSON body:
       { "record_id": "…", "delivery_quantity": 1234.56, "blob_name": "…" }
3. This function:
   a. Reads the raw PDF from Blob Storage.
   b. Invokes Azure Document Intelligence to extract text.
   c. Matches the delivery_quantity from the API body with quantities in the PDF.
   d. Optionally uses Azure OpenAI AI agent for smarter matching.
   e. Writes the JSON result to  {record_id}/processed/result.json
   f. Returns the JSON result to SAP.

Response structure (success):
  { "status": "success", "record_id": "…", "matched_quantity": 1234.56, "remarks": null, … }

Response structure (error / mismatch):
  { "status": "error", "record_id": "…", "matched_quantity": null,
    "remarks": "Delivery quantity 9999 not found in document.", … }
"""

import azure.functions as func
import json
import logging
import os
import re
from datetime import datetime, timezone

from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from ai_agent import get_validation_agent

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# ---------------------------------------------------------------------------
# Configuration from App Settings / environment
# ---------------------------------------------------------------------------
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'delivery-documents')
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', '')
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY', '')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _blob_service():
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def get_blob_url(blob_name: str) -> str:
    """Return the full URL for a blob."""
    client = _blob_service().get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME, blob=blob_name
    )
    return client.url


def extract_quantities_from_text(text: str) -> list[float]:
    """Pull all plausible numeric quantities out of OCR text."""
    pattern = r'\b\d{1,3}(?:[,\s]?\d{3})*(?:\.\d+)?\b'
    quantities = []
    for m in re.findall(pattern, text):
        cleaned = m.replace(',', '').replace(' ', '')
        try:
            quantities.append(float(cleaned))
        except ValueError:
            continue
    return quantities


def analyze_document(blob_url: str) -> tuple[str, object]:
    """Run Azure Document Intelligence on a blob URL and return (text, result)."""
    client = DocumentAnalysisClient(
        endpoint=AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_DOCUMENT_INTELLIGENCE_KEY),
    )
    poller = client.begin_analyze_document_from_url("prebuilt-document", blob_url)
    result = poller.result()
    return (result.content or ""), result


def write_result_to_blob(record_id: str, result_payload: dict) -> str:
    """
    Persist the validation result JSON to
    delivery-documents/{record_id}/processed/result.json
    Returns the blob name.
    """
    blob_name = f"{record_id}/processed/result.json"
    blob_client = _blob_service().get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME, blob=blob_name
    )
    blob_client.upload_blob(
        json.dumps(result_payload, indent=2),
        overwrite=True,
    )
    return blob_name


# ---------------------------------------------------------------------------
# HTTP Trigger: POST /api/validate
# ---------------------------------------------------------------------------
@app.route(route="api/validate", methods=["POST"])
def validate(req: func.HttpRequest) -> func.HttpResponse:
    """
    Validate a delivery quantity against the uploaded PDF.

    Body JSON:
        {
            "record_id": "<SAP record id>",
            "delivery_quantity": <number>,
            "blob_name": "<record_id>/raw/<file>"
        }

    Returns JSON with status, matched_quantity, remarks, etc.
    """
    try:
        # ---- parse request ----
        try:
            body = req.get_json()
        except ValueError:
            body = None

        if not body:
            return _json_response({'status': 'error', 'remarks': 'Request body must be JSON'}, 400)

        record_id = body.get('record_id')
        delivery_quantity = body.get('delivery_quantity')
        blob_name = body.get('blob_name')

        if not record_id or delivery_quantity is None or not blob_name:
            return _json_response({
                'status': 'error',
                'remarks': 'Missing required fields: record_id, delivery_quantity, blob_name',
            }, 400)

        try:
            delivery_quantity = float(delivery_quantity)
        except (ValueError, TypeError):
            return _json_response({
                'status': 'error',
                'record_id': record_id,
                'remarks': 'delivery_quantity must be a number',
            }, 400)

        logging.info("Validating record_id=%s  qty=%s  blob=%s", record_id, delivery_quantity, blob_name)

        # ---- read PDF via Document Intelligence ----
        blob_url = get_blob_url(blob_name)
        extracted_text, _ = analyze_document(blob_url)
        extracted_quantities = extract_quantities_from_text(extracted_text)

        # ---- match ----
        match_found = False
        matched_value = None
        for qty in extracted_quantities:
            if abs(qty - delivery_quantity) < 0.01:
                match_found = True
                matched_value = qty
                break

        # ---- optional AI agent ----
        ai_info = None
        agent = get_validation_agent()
        if agent.enabled:
            ai_info = agent.validate(extracted_text, delivery_quantity, extracted_quantities)
            if ai_info:
                match_found = ai_info.get('is_valid', match_found)
                if ai_info.get('matched_value') is not None:
                    matched_value = ai_info['matched_value']

        # ---- build result ----
        if match_found:
            result_payload = {
                'status': 'success',
                'record_id': record_id,
                'delivery_quantity': delivery_quantity,
                'matched_quantity': matched_value,
                'remarks': None,
                'extracted_quantities': extracted_quantities,
                'extracted_text_preview': extracted_text[:500],
                'ai_agent': ai_info,
                'processed_at': datetime.now(timezone.utc).isoformat(),
            }
        else:
            result_payload = {
                'status': 'error',
                'record_id': record_id,
                'delivery_quantity': delivery_quantity,
                'matched_quantity': None,
                'remarks': (
                    f"Delivery quantity {delivery_quantity} not found in document. "
                    f"Extracted values: {extracted_quantities}"
                ),
                'extracted_quantities': extracted_quantities,
                'extracted_text_preview': extracted_text[:500],
                'ai_agent': ai_info,
                'processed_at': datetime.now(timezone.utc).isoformat(),
            }

        # ---- persist result to {record_id}/processed/result.json ----
        processed_blob = write_result_to_blob(record_id, result_payload)
        result_payload['processed_blob'] = processed_blob

        logging.info("record_id=%s  status=%s", record_id, result_payload['status'])
        return _json_response(result_payload)

    except Exception as e:
        logging.exception("Validation error")
        return _json_response({'status': 'error', 'remarks': str(e)}, 500)


# ---------------------------------------------------------------------------
# HTTP Trigger: GET /api/health
# ---------------------------------------------------------------------------
@app.route(route="api/health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return _json_response({
        'status': 'healthy',
        'service': 'Delivery Quantity Validation Function',
        'document_intelligence_configured': bool(AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT),
        'storage_configured': bool(AZURE_STORAGE_CONNECTION_STRING),
        'ai_agent_enabled': get_validation_agent().enabled,
    })


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
def _json_response(body: dict, status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(body),
        status_code=status_code,
        mimetype="application/json",
    )
