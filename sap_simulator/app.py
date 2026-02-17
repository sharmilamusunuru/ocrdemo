"""
SAP Simulator - Dummy Application

This application simulates SAP behavior in the customer scenario.
It provides a web UI where users can:
1. Upload a PDF document
2. Enter discharge quantity
3. Click "Save" button

Then it:
1. Uploads the PDF to Azure Blob Storage (like SAP would)
2. Calls the Azure Validation Service API with quantity in header
3. Displays the validation result
"""

from flask import Flask, render_template, request, jsonify
import os
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Azure Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'discharge-documents')

# Validation Service Configuration
VALIDATION_SERVICE_URL = os.getenv('VALIDATION_SERVICE_URL', 'http://localhost:5001')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_to_blob_storage(file_content, filename):
    """
    Upload file to Azure Blob Storage.
    This simulates SAP uploading documents to Azure.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )
        container_client = blob_service_client.get_container_client(
            AZURE_STORAGE_CONTAINER_NAME
        )
        
        # Create container if it doesn't exist
        try:
            container_client.create_container()
        except:
            pass  # Container already exists
        
        # Generate unique blob name
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        blob_name = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
        
        # Upload blob
        blob_client = container_client.get_blob_client(blob_name)
        
        content_type = 'application/pdf' if filename.lower().endswith('.pdf') else 'image/jpeg'
        blob_client.upload_blob(
            file_content,
            content_settings=ContentSettings(content_type=content_type),
            overwrite=True
        )
        
        return blob_client.url, blob_name
    except Exception as e:
        raise Exception(f"Error uploading to blob storage: {str(e)}")


def call_validation_service(blob_name, quantity):
    """
    Call the Azure Validation Service API.
    This simulates SAP calling the Azure validation endpoint.
    """
    try:
        url = f"{VALIDATION_SERVICE_URL}/api/validate"
        
        headers = {
            'X-Discharge-Quantity': str(quantity),
            'Content-Type': 'application/json'
        }
        
        payload = {
            'blob_name': blob_name
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error calling validation service: {str(e)}")


@app.route('/')
def index():
    """Render the SAP simulator UI."""
    return render_template('sap_simulator.html')


@app.route('/simulate-sap', methods=['POST'])
def simulate_sap():
    """
    Simulate SAP behavior:
    1. Receive file upload and quantity from user
    2. Upload PDF to blob storage
    3. Call validation service API with quantity in header
    4. Return validation result
    """
    try:
        # Validate file upload
        if 'document' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['document']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Please upload PDF, PNG, JPG, or JPEG'
            }), 400
        
        # Get quantity
        quantity_str = request.form.get('quantity', 0)
        try:
            quantity = float(quantity_str)
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid quantity value'}), 400
        
        # Read file content
        filename = secure_filename(file.filename)
        file_content = file.read()
        
        # Step 1: Upload to Azure Blob Storage (simulating SAP)
        print(f"📤 SAP Simulator: Uploading {filename} to blob storage...")
        blob_url, blob_name = upload_to_blob_storage(file_content, filename)
        print(f"✅ SAP Simulator: File uploaded as {blob_name}")
        
        # Step 2: Call Azure Validation Service API (simulating SAP)
        print(f"🔍 SAP Simulator: Calling validation service with quantity={quantity}")
        validation_result = call_validation_service(blob_name, quantity)
        print(f"✅ SAP Simulator: Received validation result")
        
        # Add SAP simulation metadata
        result = {
            'success': True,
            'sap_simulation': {
                'action': 'Document uploaded and validated',
                'uploaded_file': filename,
                'blob_name': blob_name,
                'blob_url': blob_url,
                'quantity_sent': quantity
            },
            'validation_service_response': validation_result
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Test validation service connectivity
    validation_service_healthy = False
    try:
        response = requests.get(f"{VALIDATION_SERVICE_URL}/health", timeout=5)
        validation_service_healthy = response.status_code == 200
    except:
        pass
    
    return jsonify({
        'status': 'healthy',
        'service': 'SAP Simulator',
        'storage_configured': bool(AZURE_STORAGE_CONNECTION_STRING),
        'validation_service_url': VALIDATION_SERVICE_URL,
        'validation_service_reachable': validation_service_healthy
    })


if __name__ == '__main__':
    if not AZURE_STORAGE_CONNECTION_STRING:
        print("⚠️  WARNING: AZURE_STORAGE_CONNECTION_STRING not configured")
        print("   The SAP simulator will not be able to upload files to blob storage")
    
    print("🚀 SAP Simulator starting...")
    print(f"   Blob Storage: {'✓' if AZURE_STORAGE_CONNECTION_STRING else '✗'}")
    print(f"   Validation Service: {VALIDATION_SERVICE_URL}")
    print(f"   Web UI: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
