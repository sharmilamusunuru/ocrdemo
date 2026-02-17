"""
Azure Validation Service API

This service mimics the Azure backend that SAP calls to validate discharge quantities.
It receives:
- Blob storage reference via API parameter
- Expected quantity via X-Discharge-Quantity header

It performs:
1. Reads PDF from Azure Blob Storage
2. Extracts text using Azure Document Intelligence
3. Validates using AI Agent
4. Returns validation result
"""

from flask import Flask, request, jsonify
import os
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from ai_agent import get_validation_agent
import re

app = Flask(__name__)

# Azure Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'discharge-documents')
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', '')
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY', '')


def extract_quantities_from_text(text):
    """Extract numerical quantities from text."""
    pattern = r'\b\d{1,3}(?:[,\s]?\d{3})*(?:\.\d+)?\b'
    matches = re.findall(pattern, text)
    
    quantities = []
    for match in matches:
        cleaned = match.replace(',', '').replace(' ', '')
        try:
            quantities.append(float(cleaned))
        except ValueError:
            continue
    
    return quantities


def get_blob_url(blob_name):
    """Get the URL for a blob in Azure Storage."""
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME,
        blob=blob_name
    )
    return blob_client.url


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
        
        full_text = result.content if result.content else ""
        
        return full_text, result
    except Exception as e:
        raise Exception(f"Error analyzing document: {str(e)}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Azure Validation Service',
        'document_intelligence_configured': bool(AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT),
        'storage_configured': bool(AZURE_STORAGE_CONNECTION_STRING),
        'ai_agent_enabled': get_validation_agent().enabled
    })


@app.route('/api/validate', methods=['POST'])
def validate():
    """
    Validate discharge quantity against document in blob storage.
    
    Expected:
    - Header: X-Discharge-Quantity (the quantity to validate)
    - Body JSON: { "blob_name": "path/to/document.pdf" }
    
    Returns:
    - Validation result with success/failure and details
    """
    try:
        # Get quantity from header (simulating SAP sending the value)
        quantity_header = request.headers.get('X-Discharge-Quantity')
        if not quantity_header:
            return jsonify({
                'success': False,
                'error': 'Missing X-Discharge-Quantity header'
            }), 400
        
        try:
            entered_quantity = float(quantity_header)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid quantity value in header'
            }), 400
        
        # Get blob reference from request body
        request_data = request.get_json()
        if not request_data or 'blob_name' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Missing blob_name in request body'
            }), 400
        
        blob_name = request_data['blob_name']
        
        # Get blob URL
        blob_url = get_blob_url(blob_name)
        
        # Analyze document with Azure Document Intelligence
        extracted_text, analysis_result = analyze_document_with_azure_di(blob_url)
        
        # Extract quantities from text
        extracted_quantities = extract_quantities_from_text(extracted_text)
        
        # Simple validation: check for exact match
        match_found = False
        matched_value = None
        
        for qty in extracted_quantities:
            if abs(qty - entered_quantity) < 0.01:
                match_found = True
                matched_value = qty
                break
        
        # Use AI Agent for enhanced validation
        ai_validation = None
        agent = get_validation_agent()
        if agent.enabled:
            ai_validation = agent.validate(extracted_text, entered_quantity, extracted_quantities)
            
            if ai_validation:
                match_found = ai_validation.get('is_valid', match_found)
                if ai_validation.get('matched_value'):
                    matched_value = ai_validation.get('matched_value')
        
        # Prepare response
        result = {
            'success': True,
            'validation_result': {
                'passed': match_found,
                'entered_quantity': entered_quantity,
                'matched_value': matched_value,
                'extracted_quantities': extracted_quantities,
                'extracted_text_preview': extracted_text[:500],
                'blob_name': blob_name,
                'blob_url': blob_url
            },
            'ai_agent': {
                'used': ai_validation is not None,
                'confidence': ai_validation.get('confidence') if ai_validation else None,
                'reasoning': ai_validation.get('reasoning') if ai_validation else None,
                'field_location': ai_validation.get('field_location') if ai_validation else None
            } if ai_validation else None
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze-structure', methods=['POST'])
def analyze_structure():
    """
    Analyze document structure using AI Agent.
    Helpful for understanding what fields are in the document.
    """
    try:
        request_data = request.get_json()
        if not request_data or 'blob_name' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Missing blob_name in request body'
            }), 400
        
        blob_name = request_data['blob_name']
        blob_url = get_blob_url(blob_name)
        
        # Extract text
        extracted_text, _ = analyze_document_with_azure_di(blob_url)
        
        # Use AI agent to analyze structure
        agent = get_validation_agent()
        if not agent.enabled:
            return jsonify({
                'success': False,
                'error': 'AI Agent not configured'
            }), 503
        
        structure = agent.analyze_document_structure(extracted_text)
        
        return jsonify({
            'success': True,
            'blob_name': blob_name,
            'document_structure': structure,
            'text_preview': extracted_text[:500]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Check configuration
    if not AZURE_STORAGE_CONNECTION_STRING:
        print("⚠️  WARNING: AZURE_STORAGE_CONNECTION_STRING not configured")
    if not AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:
        print("⚠️  WARNING: AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT not configured")
    
    print("🚀 Azure Validation Service starting...")
    print(f"   Document Intelligence: {'✓' if AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT else '✗'}")
    print(f"   Blob Storage: {'✓' if AZURE_STORAGE_CONNECTION_STRING else '✗'}")
    print(f"   AI Agent: {'✓' if get_validation_agent().enabled else '✗'}")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
