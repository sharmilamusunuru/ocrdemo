from flask import Flask, render_template, request, jsonify
import os
import re
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import pdf2image
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_quantities_from_text(text):
    """Extract numerical quantities from OCR text."""
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

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using OCR."""
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)
        
        all_text = []
        for i, image in enumerate(images):
            # Perform OCR on each page
            text = pytesseract.image_to_string(image)
            all_text.append(text)
        
        return '\n'.join(all_text)
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def extract_text_from_image(image_path):
    """Extract text from image using OCR."""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

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
        
        # Get entered quantity
        try:
            entered_quantity = float(request.form.get('quantity', 0))
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid quantity value'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                extracted_text = extract_text_from_pdf(filepath)
            else:
                extracted_text = extract_text_from_image(filepath)
            
            # Extract quantities from the text
            extracted_quantities = extract_quantities_from_text(extracted_text)
            
            # Check if entered quantity matches any extracted quantity
            match_found = False
            matched_value = None
            
            for qty in extracted_quantities:
                # Allow small floating point differences
                if abs(qty - entered_quantity) < 0.01:
                    match_found = True
                    matched_value = qty
                    break
            
            result = {
                'success': True,
                'validation_passed': match_found,
                'entered_quantity': entered_quantity,
                'extracted_quantities': extracted_quantities,
                'matched_value': matched_value,
                'extracted_text': extracted_text[:500]  # First 500 chars for debugging
            }
            
            return jsonify(result)
        
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
