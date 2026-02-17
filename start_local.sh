#!/bin/bash
# Local testing startup script

echo "🚀 Starting OCR Demo in LOCAL MODE"
echo "======================================"
echo ""
echo "This will run the application WITHOUT Azure services."
echo "Perfect for local development and testing!"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Create local storage directory
echo "📁 Creating local storage directory..."
mkdir -p local_storage/documents

# Check if Tesseract is installed (optional but recommended)
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found. OCR features will be limited."
    echo "   Install with: sudo apt-get install tesseract-ocr (Linux)"
    echo "   Or: brew install tesseract (macOS)"
else
    echo "✅ Tesseract OCR found"
fi

# Install dependencies if needed
echo ""
echo "📦 Checking dependencies..."

if [ ! -d "sap_simulator/__pycache__" ] && [ ! -d "validation_service/__pycache__" ]; then
    echo "Installing Python dependencies..."
    
    echo "  → SAP Simulator dependencies..."
    cd sap_simulator
    pip install -q -r requirements.txt
    pip install -q pytesseract pillow pdf2image  # For local OCR
    cd ..
    
    echo "  → Validation Service dependencies..."
    cd validation_service
    pip install -q -r requirements.txt
    pip install -q pytesseract pillow pdf2image  # For local OCR
    cd ..
    
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Generate sample documents if they don't exist
if [ ! -f "sample_discharge_document.pdf" ]; then
    echo ""
    echo "📄 Generating sample test documents..."
    pip install -q reportlab
    python create_sample_docs.py
fi

echo ""
echo "🎬 Starting services..."
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $VALIDATION_PID $SAP_PID 2>/dev/null
    wait $VALIDATION_PID $SAP_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Start Validation Service in background
echo "Starting Validation Service on http://localhost:5001..."
cd validation_service
python app_local.py &
VALIDATION_PID=$!
cd ..

# Wait for validation service to start
echo "⏳ Waiting for Validation Service to start..."
sleep 3

# Check if validation service is running
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ Validation Service is running"
else
    echo "⚠️  Validation Service may not have started successfully"
fi

# Start SAP Simulator in background
echo ""
echo "Starting SAP Simulator on http://localhost:5000..."
cd sap_simulator
python app_local.py &
SAP_PID=$!
cd ..

# Wait for SAP simulator to start
echo "⏳ Waiting for SAP Simulator to start..."
sleep 3

# Check if SAP simulator is running
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ SAP Simulator is running"
else
    echo "⚠️  SAP Simulator may not have started successfully"
fi

echo ""
echo "=========================================="
echo "✨ Application is ready!"
echo "=========================================="
echo ""
echo "📱 Open in browser: http://localhost:5000"
echo ""
echo "📋 Available Endpoints:"
echo "   SAP Simulator UI:     http://localhost:5000"
echo "   SAP Health Check:     http://localhost:5000/health"
echo "   Validation API:       http://localhost:5001/api/validate"
echo "   Validation Health:    http://localhost:5001/health"
echo ""
echo "📝 Test Files Available:"
echo "   - sample_discharge_document.pdf (quantity: 1234.56)"
echo "   - sample_discharge_document_2.pdf (quantity: 5678.90)"
echo "   - sample_discharge_document_3.pdf (quantity: 100.00)"
echo ""
echo "🧪 Quick Test:"
echo "   1. Open http://localhost:5000"
echo "   2. Upload sample_discharge_document.pdf"
echo "   3. Enter quantity: 1234.56"
echo "   4. Click 'Save'"
echo "   5. Should show ✅ Validation Successful!"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="
echo ""

# Wait for both processes
wait $VALIDATION_PID $SAP_PID
