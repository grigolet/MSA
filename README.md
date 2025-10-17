# Metal Slug Awakening - OCR Player Power Analysis

A Streamlit web application that processes screenshots from the Metal Slug Awakening mobile game to extract player names and power levels using OCR (Optical Character Recognition).

## Features

- **Image Upload**: Upload up to 16 screenshots from the game
- **Automatic Cropping**: Crops images to focus on the relevant player data area
- **OCR Processing**: Extracts text using EasyOCR with English language support
- **Data Cleaning**: Automatically cleans and parses player names and power levels
- **Interactive Table**: Displays results in a sortable, searchable table
- **Malformed Detection**: Flags potentially malformed entries for manual review
- **Export Options**: Download results as CSV or copy-paste ready format

## Requirements

### System Dependencies
- Python 3.11+
- ImageMagick (for image cropping)

### Python Dependencies
See `requirements.txt` for the complete list. Main dependencies include:
- streamlit
- pandas
- easyocr
- opencv-python
- Pillow

## Installation & Setup

### Option 1: Local Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MSA
   ```

2. **Install system dependencies**:
   
   **Ubuntu/Debian**:
   ```bash
   sudo apt-get update
   sudo apt-get install imagemagick
   ```
   
   **macOS** (using Homebrew):
   ```bash
   brew install imagemagick
   ```
   
   **Windows**:
   Download and install ImageMagick from: https://imagemagick.org/script/download.php#windows

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Access the application**:
   Open your browser and go to `http://localhost:8501`

### Option 2: Docker Deployment

1. **Build the Docker image**:
   ```bash
   docker build -t msa-ocr .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 msa-ocr
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:8501`

## Usage

1. **Take Screenshots**: Capture screenshots from Metal Slug Awakening showing the member list with player names and power levels.

2. **Upload Images**: Use the file uploader to select up to 16 screenshots (JPG, JPEG, or PNG format).

3. **Process Images**: Click the "Process Images" button to:
   - Automatically crop images to focus on the player data area
   - Run OCR to extract text
   - Clean and parse player names and power levels
   - Detect potentially malformed entries

4. **Review Results**: 
   - View the processed data in an interactive table
   - Check for any flagged malformed entries
   - Review summary statistics

5. **Export Data**:
   - Download results as a CSV file
   - Copy data in a ready-to-paste format

## Project Structure

```
MSA/
├── app.py                 # Main Streamlit application
├── cleantext.py          # OCR text cleaning and parsing logic
├── ocr.py               # Alternative OCR implementation (PaddleOCR)
├── crop.sh              # Shell script for batch image cropping
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── README.md            # This file
└── screenshots/         # Sample screenshots and processed data
    ├── cropped/         # Cropped images output
    └── *.jpg            # Original screenshots
```

## Configuration

The OCR processing behavior can be configured by modifying variables in `cleantext.py`:

- `MIN_DIGITS`: Minimum number of digits required for a valid power value (default: 6)
- `STRICT_MIN_POWER`: Minimum power threshold; entries below this are flagged as suspects (default: 3,000,000)
- `DROP_TOKENS`: Set of tokens to ignore during name parsing (roles, common terms, etc.)

## Troubleshooting

### Common Issues

1. **ImageMagick not found**:
   - Ensure ImageMagick is installed and the `magick` command is available in your PATH
   - On some systems, the command might be `convert` instead of `magick`

2. **OCR accuracy issues**:
   - Ensure screenshots are clear and well-lit
   - The cropping parameters are tuned for specific screenshot dimensions
   - You may need to adjust cropping parameters in the `crop_images()` function

3. **Memory issues with large images**:
   - Reduce image sizes before uploading
   - Process fewer images at once

4. **Docker build issues**:
   - Ensure you have sufficient disk space
   - Check that Docker has enough memory allocated

### Performance Tips

- Use high-quality, well-lit screenshots for better OCR accuracy
- Crop images manually before uploading if the automatic cropping doesn't work well
- Process images in smaller batches if you encounter memory issues

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the application thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational and personal use. Please respect the terms of service of Metal Slug Awakening when using this tool.

## Acknowledgments

- Uses EasyOCR for text recognition
- Built with Streamlit for the web interface
- ImageMagick for image processing
