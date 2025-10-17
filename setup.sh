#!/bin/bash
# GitHub Setup Script for Metal Slug Awakening OCR

echo "🚀 Metal Slug Awakening OCR - GitHub Setup"
echo "=========================================="

# Check if this is a fresh clone
if [ ! -d ".git" ]; then
    echo "❌ Error: This script should be run in the root of the git repository"
    exit 1
fi

echo "✅ Repository structure verified"

# Create sample directories (empty, just for reference)
echo "📁 Creating sample directory structure..."
mkdir -p sample_structure/screenshots/{cropped}
echo "# Place your game screenshots here" > sample_structure/screenshots/README.md
echo "# Cropped images will be generated here automatically" > sample_structure/screenshots/cropped/README.md

# Verify Python dependencies
echo "🐍 Checking Python environment..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Docker
echo "🐳 Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker found: $(docker --version)"
else
    echo "⚠️  Docker not found. Docker deployment will not be available."
fi

# Check ImageMagick
echo "🖼️  Checking ImageMagick..."
if command -v magick &> /dev/null || command -v convert &> /dev/null; then
    echo "✅ ImageMagick found"
else
    echo "⚠️  ImageMagick not found. Image cropping will not work."
    echo "   Install with: sudo apt-get install imagemagick (Ubuntu/Debian)"
    echo "   Or: brew install imagemagick (macOS)"
fi

echo ""
echo "🎯 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Run the application: streamlit run app.py"
echo "3. Upload your Metal Slug Awakening screenshots"
echo ""
echo "For Docker deployment:"
echo "1. Build: docker build -t msa-ocr ."
echo "2. Run: docker run -p 8501:8501 msa-ocr"
echo ""
echo "📝 Remember: Never commit actual game screenshots or player data!"
