"""
Validation Service - Local Development Version

This version works WITHOUT Azure services for local testing.
Uses local file storage and mock AI responses.
"""

from flask import Flask, request, jsonify
import os
import re
from pathlib import Path

# For local OCR fallback
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Tesseract not available. Install with: pip install pytesseract pillow pdf2image")

app = Flask(__name__)

# Local Configuration
LOCAL_STORAGE_PATH = os.getenv('LOCAL_STORAGE_PATH', './local_storage/documents')
Path(LOCAL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)


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


def extract_text_from_pdf_local(pdf_path):
    """Extract text from PDF using Tesseract (local fallback)."""
    if not TESSERACT_AVAILABLE:
        return "Tesseract OCR not available. Please install: pip install pytesseract pillow pdf2image"
    
    try:
        images = pdf2image.convert_from_path(pdf_path)
        all_text = []
        for image in images:
            text = pytesseract.image_to_string(image)
            all_text.append(text)
        return '\n'.join(all_text)
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def mock_ai_validation(extracted_text, entered_quantity, extracted_quantities):
    """Mock AI validation for local testing."""
    # Simple mock: check if quantity is in extracted list
    match = any(abs(q - entered_quantity) < 0.01 for q in extracted_quantities)
    
    return {
        'is_valid': match,
        'matched_value': entered_quantity if match else None,
        'confidence': 95 if match else 30,
        'reasoning': f"{'Found' if match else 'Did not find'} the entered quantity {entered_quantity} in the document. This is a MOCK AI response for local testing.",
        'field_location': 'Mock location - using local mode without Azure OpenAI'
    }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Validation Service (Local Mode)',
        'mode': 'local',
        'tesseract_available': TESSERACT_AVAILABLE,
        'storage_path': LOCAL_STORAGE_PATH
    })


@app.route('/api/validate', methods=['POST'])
def validate():
    """
    Validate discharge quantity against document (LOCAL MODE).
    
    Expected:
    - Header: X-Discharge-Quantity
    - Body JSON: { "blob_name": "filename.pdf" }
    """
    try:
        # Get quantity from header
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
        local_file_path = os.path.join(LOCAL_STORAGE_PATH, blob_name)
        
        # Check if file exists
        if not os.path.exists(local_file_path):
            return jsonify({
                'success': False,
                'error': f'File not found: {blob_name}'
            }), 404
        
        # Extract text using Tesseract (local OCR)
        print(f"📄 Extracting text from: {local_file_path}")
        extracted_text = extract_text_from_pdf_local(local_file_path)
        
        # Extract quantities from text
        extracted_quantities = extract_quantities_from_text(extracted_text)
        print(f"🔍 Found quantities: {extracted_quantities}")
        
        # Simple validation: check for exact match
        match_found = False
        matched_value = None
        
        for qty in extracted_quantities:
            if abs(qty - entered_quantity) < 0.01:
                match_found = True
                matched_value = qty
                break
        
        # Mock AI validation (simulates Azure OpenAI)
        ai_validation = mock_ai_validation(extracted_text, entered_quantity, extracted_quantities)
        
        # Use AI validation result
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
                'blob_url': f'file://{local_file_path}'
            },
            'ai_agent': {
                'used': True,
                'mode': 'mock',
                'confidence': ai_validation.get('confidence'),
                'reasoning': ai_validation.get('reasoning'),
                'field_location': ai_validation.get('field_location')
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("🚀 Validation Service (Local Mode) starting...")
    print(f"   Storage Path: {LOCAL_STORAGE_PATH}")
    print(f"   Tesseract OCR: {'✓' if TESSERACT_AVAILABLE else '✗ (install for OCR)'}")
    print(f"   Mode: LOCAL (no Azure services required)")
    print(f"   API: http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
