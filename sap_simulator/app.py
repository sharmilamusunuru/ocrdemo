"""
SAP Simulator – Dummy Application

Mimics the real SAP workflow:
1. User enters a delivery quantity and uploads a delivery-order PDF.
2. On "Save" the tool:
   a. Generates a unique record_id (like a SAP document number).
   b. Stores the record in an in-memory "SAP DB".
   c. Uploads the PDF to Azure Blob Storage under
      delivery-documents/{record_id}/raw/{filename}.
   d. Calls the Azure Validation Function API with
      { record_id, delivery_quantity, blob_name }.
3. The Azure Function processes the PDF, writes results to
   {record_id}/processed/result.json, and returns a JSON response.
4. The SAP simulator displays that response to the user.
"""

from flask import Flask, render_template, request, jsonify
import os
import time
import threading
import requests
from functools import wraps
from collections import defaultdict
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Azure Configuration
AZURE_STORAGE_ACCOUNT_URL = os.getenv('AZURE_STORAGE_ACCOUNT_URL', '')
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'delivery-documents')

# Validation Service Configuration (Azure Function App URL)
VALIDATION_SERVICE_URL = os.getenv('VALIDATION_SERVICE_URL', 'http://localhost:7071')
VALIDATION_SERVICE_KEY = os.getenv('VALIDATION_SERVICE_KEY', '')

# ---------------------------------------------------------------------------
# In-memory SAP "database" (with thread lock)
# ---------------------------------------------------------------------------
SAP_DB: dict = {}  # record_id -> { record_id, delivery_quantity, blob_name, … }
_sap_db_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Simple in-memory rate limiter
# ---------------------------------------------------------------------------
_rate_limit_store: dict = defaultdict(list)
_rate_limit_lock = threading.Lock()


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Decorator that rate-limits requests per client IP."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr or 'unknown'
            now = time.time()
            with _rate_limit_lock:
                _rate_limit_store[client_ip] = [
                    t for t in _rate_limit_store[client_ip]
                    if t > now - window_seconds
                ]
                if len(_rate_limit_store[client_ip]) >= max_requests:
                    return jsonify({'success': False, 'error': 'Rate limit exceeded. Please try again later.'}), 429
                _rate_limit_store[client_ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def _new_record_id() -> str:
    """Generate a SAP-style record id: YYYYMMDD-<hex8>."""
    ts = datetime.now(timezone.utc).strftime('%Y%m%d')
    return f"{ts}-{uuid.uuid4().hex[:8].upper()}"


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Blob helpers
# ---------------------------------------------------------------------------
def upload_pdf_to_blob(file_content: bytes, filename: str, record_id: str):
    """
    Upload the raw PDF into delivery-documents/{record_id}/raw/{filename}.
    Returns (blob_url, blob_name).
    """
    blob_service_client = (
        BlobServiceClient(account_url=AZURE_STORAGE_ACCOUNT_URL, credential=DefaultAzureCredential())
        if AZURE_STORAGE_ACCOUNT_URL
        else BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    )
    container_client = blob_service_client.get_container_client(
        AZURE_STORAGE_CONTAINER_NAME
    )

    # Ensure the container exists
    try:
        container_client.create_container()
    except Exception:
        pass  # already exists

    blob_name = f"{record_id}/raw/{filename}"
    blob_client = container_client.get_blob_client(blob_name)

    content_type = 'application/pdf' if filename.lower().endswith('.pdf') else 'image/jpeg'
    blob_client.upload_blob(
        file_content,
        content_settings=ContentSettings(content_type=content_type),
        overwrite=True,
    )

    return blob_client.url, blob_name


# ---------------------------------------------------------------------------
# Call Azure Validation Function
# ---------------------------------------------------------------------------
def call_validation_service(record_id: str, delivery_quantity: float, blob_name: str) -> dict:
    """
    POST to the Azure Function with field details in the JSON body.
    """
    url = f"{VALIDATION_SERVICE_URL}/api/validate"

    payload = {
        'record_id': record_id,
        'delivery_quantity': delivery_quantity,
        'blob_name': blob_name,
    }

    headers = {}
    if VALIDATION_SERVICE_KEY:
        headers['x-functions-key'] = VALIDATION_SERVICE_KEY

    response = requests.post(url, json=payload, headers=headers, timeout=300)

    # Try to read JSON body even on error status codes so we surface
    # the actual error message from the validation function.
    try:
        result = response.json()
    except ValueError:
        if response.status_code == 502:
            raise RuntimeError(
                "Validation service returned 502 Bad Gateway. "
                "The Function App may still be deploying or restarting. "
                "Please wait 1-2 minutes and try again."
            )
        response.raise_for_status()
        raise RuntimeError(f"Validation service returned non-JSON (HTTP {response.status_code})")

    if response.status_code >= 500:
        detail = result.get('remarks') or result.get('error') or str(result)
        raise RuntimeError(f"Validation service error: {detail}")

    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    """Render the SAP simulator UI."""
    return render_template('sap_simulator.html')


@app.route('/simulate-sap', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60)
def simulate_sap():
    """
    Full SAP save flow:
    1. Validate inputs
    2. Create record_id and store in SAP DB
    3. Upload PDF to  {record_id}/raw/
    4. Call Azure Function API
    5. Return combined result to the UI
    """
    try:
        # --- validate file ---
        if 'document' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['document']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Please upload PDF, PNG, JPG, or JPEG',
            }), 400

        # --- validate quantity ---
        quantity_str = request.form.get('quantity', '')
        try:
            delivery_quantity = float(quantity_str)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid quantity value'}), 400

        filename = secure_filename(file.filename)
        file_content = file.read()

        # Step 1 – create a unique record_id (SAP DB)
        record_id = _new_record_id()

        # Step 2 – upload PDF to blob   {record_id}/raw/{filename}
        print(f"[SAP] Uploading {filename} -> {record_id}/raw/ ...")
        blob_url, blob_name = upload_pdf_to_blob(file_content, filename, record_id)
        print(f"[SAP] Uploaded: {blob_name}")

        # Step 3 – persist record in SAP DB
        with _sap_db_lock:
            SAP_DB[record_id] = {
                'record_id': record_id,
                'delivery_quantity': delivery_quantity,
                'filename': filename,
                'blob_name': blob_name,
                'blob_url': blob_url,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'validation_status': 'pending',
            }

        # Step 4 – call Azure Validation Function API
        print(f"[SAP] Calling validation API for record_id={record_id}, qty={delivery_quantity}")
        validation_response = call_validation_service(record_id, delivery_quantity, blob_name)
        print(f"[SAP] Received validation response")

        # Step 5 – update SAP DB with result
        with _sap_db_lock:
            SAP_DB[record_id]['validation_status'] = (
                'success' if validation_response.get('status') == 'success' else 'error'
            )
            SAP_DB[record_id]['validation_response'] = validation_response

        # Build response for the UI
        result = {
            'success': True,
            'sap_record': {
                'record_id': record_id,
                'delivery_quantity': delivery_quantity,
                'uploaded_file': filename,
                'blob_name': blob_name,
                'blob_url': blob_url,
            },
            'validation_response': validation_response,
        }
        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': 'Validation service is temporarily unavailable. Please try again later.'}), 502
    except Exception as e:
        app.logger.exception("Unexpected error in simulate_sap")
        return jsonify({'success': False, 'error': 'An internal error occurred. Please try again later.'}), 500


@app.route('/records', methods=['GET'])
def list_records():
    """Return all SAP records (for debugging / demo)."""
    with _sap_db_lock:
        return jsonify({'records': list(SAP_DB.values())})


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    validation_service_healthy = False
    try:
        resp = requests.get(f"{VALIDATION_SERVICE_URL}/api/health", timeout=5)
        validation_service_healthy = resp.status_code == 200
    except Exception:
        pass

    return jsonify({
        'status': 'healthy',
        'service': 'SAP Simulator',
        'storage_configured': bool(AZURE_STORAGE_ACCOUNT_URL or AZURE_STORAGE_CONNECTION_STRING),
        'validation_service_url': VALIDATION_SERVICE_URL,
        'validation_service_reachable': validation_service_healthy,
        'total_records': len(SAP_DB),
    })


if __name__ == '__main__':
    if not AZURE_STORAGE_ACCOUNT_URL and not AZURE_STORAGE_CONNECTION_STRING:
        print("WARNING: AZURE_STORAGE_ACCOUNT_URL / AZURE_STORAGE_CONNECTION_STRING not configured")
        print("  The SAP simulator will not be able to upload files to blob storage")

    print("SAP Simulator starting...")
    print(f"  Blob Storage: {'configured' if (AZURE_STORAGE_ACCOUNT_URL or AZURE_STORAGE_CONNECTION_STRING) else 'NOT configured'}")
    print(f"  Validation Service: {VALIDATION_SERVICE_URL}")
    print(f"  Web UI: http://localhost:5000")

    app.run(debug=False, host='0.0.0.0', port=5000)
