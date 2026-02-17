"""
SAP Simulator - Local Development Version

This version works WITHOUT Azure Blob Storage for local testing.
Uses local file storage instead.
"""

from flask import Flask, render_template, request, jsonify
import os
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from pathlib import Path
import shutil

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Local Configuration
LOCAL_STORAGE_PATH = os.getenv('LOCAL_STORAGE_PATH', './local_storage/documents')
VALIDATION_SERVICE_URL = os.getenv('VALIDATION_SERVICE_URL', 'http://localhost:5001')

# Create storage directory
Path(LOCAL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_to_local_storage(file_content, filename):
    """
    Save file to local filesystem (simulating blob storage).
    """
    try:
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        blob_name = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
        
        # Save file
        filepath = os.path.join(LOCAL_STORAGE_PATH, blob_name)
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        blob_url = f"file://{filepath}"
        return blob_url, blob_name
    except Exception as e:
        raise Exception(f"Error saving to local storage: {str(e)}")


def call_validation_service(blob_name, quantity):
    """
    Call the Validation Service API (local mode).
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
    Simulate SAP behavior (LOCAL MODE):
    1. Receive file upload and quantity from user
    2. Save PDF to local storage
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
        
        # Step 1: Save to local storage (simulating Azure Blob Storage)
        print(f"📤 SAP Simulator: Saving {filename} to local storage...")
        blob_url, blob_name = save_to_local_storage(file_content, filename)
        print(f"✅ SAP Simulator: File saved as {blob_name}")
        
        # Step 2: Call Validation Service API (simulating SAP API call)
        print(f"🔍 SAP Simulator: Calling validation service with quantity={quantity}")
        validation_result = call_validation_service(blob_name, quantity)
        print(f"✅ SAP Simulator: Received validation result")
        
        # Add SAP simulation metadata
        result = {
            'success': True,
            'sap_simulation': {
                'action': 'Document uploaded and validated (LOCAL MODE)',
                'uploaded_file': filename,
                'blob_name': blob_name,
                'blob_url': blob_url,
                'quantity_sent': quantity,
                'mode': 'local'
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
        'service': 'SAP Simulator (Local Mode)',
        'mode': 'local',
        'storage_path': LOCAL_STORAGE_PATH,
        'validation_service_url': VALIDATION_SERVICE_URL,
        'validation_service_reachable': validation_service_healthy
    })


if __name__ == '__main__':
    print("🚀 SAP Simulator (Local Mode) starting...")
    print(f"   Storage Path: {LOCAL_STORAGE_PATH}")
    print(f"   Validation Service: {VALIDATION_SERVICE_URL}")
    print(f"   Mode: LOCAL (no Azure Blob Storage required)")
    print(f"   Web UI: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
