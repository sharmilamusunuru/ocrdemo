# OCR Demo - Discharge Quantity Validation App

A dummy application that mimics SAP tool behavior for validating discharge quantities against values extracted from PDF documents using OCR (Optical Character Recognition).

## Overview

This application allows users to:
- Upload PDF documents containing discharge quantities
- Enter the expected quantity value manually
- Automatically extract quantities from the uploaded document using OCR
- Validate if the entered quantity matches any value found in the document
- Display success/failure status based on the validation result

## Features

- 📄 **PDF & Image Upload**: Support for PDF, PNG, JPG, and JPEG formats
- 🔍 **OCR Processing**: Uses Tesseract OCR for text extraction from documents
- ✅ **Automated Validation**: Compares entered values with extracted quantities
- 🎨 **Modern UI**: Clean, user-friendly interface with real-time feedback
- 🚀 **Lightweight**: Simple Flask-based application, easy to deploy

## Prerequisites

Before running this application, ensure you have the following installed:

1. **Python 3.8+**
2. **Tesseract OCR**
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
3. **Poppler** (for PDF processing)
   - **Ubuntu/Debian**: `sudo apt-get install poppler-utils`
   - **macOS**: `brew install poppler`
   - **Windows**: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sharmilamusunuru/ocrdemo.git
cd ocrdemo
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the application:
   - Click on the upload area to select a PDF or image file containing quantities
   - Enter the expected discharge quantity in the text field
   - Click "Validate & Save" to process the document
   - View the validation result showing success or failure

## How It Works

1. **Document Upload**: User uploads a PDF or image document
2. **OCR Processing**: The application uses Tesseract OCR to extract text from the document
3. **Quantity Extraction**: Numerical values are extracted from the OCR text using pattern matching
4. **Validation**: The entered quantity is compared against all extracted quantities
5. **Result Display**: Shows whether a match was found (success) or not (failure)

## API Endpoints

### `GET /`
Returns the main HTML interface

### `POST /validate`
Validates the uploaded document against the entered quantity

**Request:**
- `document` (file): PDF or image file
- `quantity` (number): Expected quantity value

**Response:**
```json
{
    "success": true,
    "validation_passed": true,
    "entered_quantity": 1234.56,
    "extracted_quantities": [1234.56, 789.12],
    "matched_value": 1234.56,
    "extracted_text": "Sample text..."
}
```

## Project Structure

```
ocrdemo/
├── app.py                  # Flask application backend
├── templates/
│   └── index.html         # Frontend UI
├── requirements.txt       # Python dependencies
└── README.md             # Documentation
```

## Security Considerations

- File size limited to 16MB to prevent abuse
- Only specific file types allowed (PDF, PNG, JPG, JPEG)
- Uploaded files are automatically deleted after processing
- Input validation for quantity values

## Testing

To test the application:

1. Create a sample PDF or image with a number on it (e.g., using any document editor)
2. Upload the file through the web interface
3. Enter the same number in the quantity field
4. Submit and verify the validation passes

## Troubleshooting

**Issue: "Tesseract not found"**
- Ensure Tesseract OCR is installed and added to your system PATH

**Issue: "PDF processing failed"**
- Verify Poppler is installed correctly
- Check if the PDF file is not corrupted

**Issue: "No quantities extracted"**
- Ensure the document has clear, readable numbers
- Try with a higher quality scan or image

## Future Enhancements

- Support for more document formats
- Advanced OCR with Azure Form Recognizer or AWS Textract
- Database storage for validation history
- User authentication and multi-user support
- Export validation results to CSV/Excel
- Integration with actual SAP systems

## License

MIT License

## Author

Sharmila Musunuru