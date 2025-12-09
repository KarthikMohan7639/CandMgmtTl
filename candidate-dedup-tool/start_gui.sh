#!/bin/bash
# Startup script for Candidate Deduplication Tool GUI

echo "==================================="
echo "Candidate Deduplication Tool - GUI"
echo "==================================="
echo ""

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if PyQt5 is installed
if ! python -c "import PyQt5" 2>/dev/null; then
    echo "⚠ PyQt5 not found. Installing..."
    pip install PyQt5>=5.15.0
fi

echo ""
echo "✓ Starting application..."
echo ""

# Run the application
python -m app --debug

echo ""
echo "Application closed."
