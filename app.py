from flask import Flask, render_template, request, jsonify
import os
import re
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

# Azure SDK imports
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Import AI Agent
from ai_agent import get_validation_agent

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Azure Configuration from environment variables
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'discharge-documents')
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', '')
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY', '')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_blob_storage(file_content, filename):
    """Upload file to Azure Blob Storage and return the blob URL."""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
        
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
        
        # Set content type based on file extension
        content_type = 'application/pdf' if filename.lower().endswith('.pdf') else 'image/jpeg'
        blob_client.upload_blob(
            file_content,
            content_settings=ContentSettings(content_type=content_type),
            overwrite=True
        )
        
        return blob_client.url, blob_name
    except Exception as e:
        raise Exception(f"Error uploading to blob storage: {str(e)}")

def analyze_document_with_azure_di(blob_url):
    """Analyze document using Azure Document Intelligence."""
    try:
        document_analysis_client = DocumentAnalysisClient(
            endpoint=AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(AZURE_DOCUMENT_INTELLIGENCE_KEY)
        )
        
        poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-document", blob_url
        )
        result = poller.result()
        
        # Extract all text content
        full_text = ""
        if result.content:
            full_text = result.content
        
        return full_text, result
    except Exception as e:
        raise Exception(f"Error analyzing document: {str(e)}")

def extract_quantities_from_text(text):
    """Extract numerical quantities from text."""
    # Look for numbers with optional decimal points and units
    # Pattern matches: 123, 123.45, 123,456.78, etc.
    pattern = r'\b\d{1,3}(?:[,\s]?\d{3})*(?:\.\d+)?\b'
    matches = re.findall(pattern, text)
    
    # Clean and convert to float
    quantities = []
    for match in matches:
        # Remove commas and spaces
        cleaned = match.replace(',', '').replace(' ', '')
        try:
            quantities.append(float(cleaned))
        except ValueError:
            continue
    
    return quantities

def call_ai_agent_for_validation(extracted_text, entered_quantity, extracted_quantities):
    """
    AI Agent that uses Azure OpenAI to intelligently validate quantities.
    This agent can understand context and provide more sophisticated validation.
    """
    agent = get_validation_agent()
    return agent.validate(extracted_text, entered_quantity, extracted_quantities)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    try:
        # Check if file was uploaded
        if 'document' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['document']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload PDF, PNG, JPG, or JPEG'}), 400
        
        # Get entered quantity from header or form
        entered_quantity_str = request.headers.get('X-Discharge-Quantity') or request.form.get('quantity', 0)
        try:
            entered_quantity = float(entered_quantity_str)
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid quantity value'}), 400
        
        # Read file content
        filename = secure_filename(file.filename)
        file_content = file.read()
        
        # Upload to Azure Blob Storage
        blob_url, blob_name = upload_to_blob_storage(file_content, filename)
        
        # Analyze document with Azure Document Intelligence
        extracted_text, analysis_result = analyze_document_with_azure_di(blob_url)
        
        # Extract quantities from the text
        extracted_quantities = extract_quantities_from_text(extracted_text)
        
        # Check if entered quantity matches any extracted quantity (simple validation)
        match_found = False
        matched_value = None
        
        for qty in extracted_quantities:
            # Allow small floating point differences
            if abs(qty - entered_quantity) < 0.01:
                match_found = True
                matched_value = qty
                break
        
        # Use AI Agent for enhanced validation (if configured)
        ai_validation = None
        if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY:
            ai_validation = call_ai_agent_for_validation(extracted_text, entered_quantity, extracted_quantities)
            
            # Override simple validation with AI validation if available
            if ai_validation:
                match_found = ai_validation.get('is_valid', match_found)
                if ai_validation.get('matched_value'):
                    matched_value = ai_validation.get('matched_value')
        
        result = {
            'success': True,
            'validation_passed': match_found,
            'entered_quantity': entered_quantity,
            'extracted_quantities': extracted_quantities,
            'matched_value': matched_value,
            'extracted_text': extracted_text[:500],  # First 500 chars for debugging
            'blob_url': blob_url,
            'blob_name': blob_name,
            'ai_agent_used': ai_validation is not None,
            'ai_confidence': ai_validation.get('confidence') if ai_validation else None,
            'ai_reasoning': ai_validation.get('reasoning') if ai_validation else None
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Check if Azure credentials are configured
    if not AZURE_STORAGE_CONNECTION_STRING:
        print("WARNING: AZURE_STORAGE_CONNECTION_STRING not configured. Running in local mode.")
    if not AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:
        print("WARNING: AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT not configured.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

