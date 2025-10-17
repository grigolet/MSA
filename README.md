# Metal Slug Awakening - OCR Text Cleaning

A Streamlit web application that processes screenshots from the Metal Slug Awakening game to extract player names and power levels from the members club.

## Features

- **Multi-image Upload**: Accept up to 16 screenshots at once
- **Automatic Cropping**: Uses ImageMagick to extract the relevant portions of screenshots
- **OCR Processing**: Extracts text using EasyOCR with specialized cleaning algorithms
- **Data Validation**: Identifies potentially malformed entries
- **Export Options**: Download results as CSV or copy-paste format
- **Docker Support**: Easy deployment with Docker

## Requirements

- Python 3.11+
- ImageMagick (for image cropping)
- Dependencies listed in `requirements.txt`

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ImageMagick:**
   - Ubuntu/Debian: `sudo apt-get install imagemagick`
   - macOS: `brew install imagemagick`
   - Windows: Download from [ImageMagick website](https://imagemagick.org/script/download.php)

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

### Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t msa-ocr .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 msa-ocr
   ```

3. **Access the application** at `http://localhost:8501`

## Usage

1. **Upload Screenshots**: Drag and drop or select up to 16 images from your Metal Slug Awakening members club
2. **Preview Images**: Optionally view the uploaded images before processing
3. **Process**: Click "Process Images" to start the OCR pipeline
4. **Review Results**: View the extracted player data in a sorted table
5. **Export**: Download as CSV or copy the text format for spreadsheets

## How It Works

1. **Image Cropping**: Uploaded images are cropped to extract the members list area (417x380 pixels starting at position 447,170)
2. **OCR Processing**: EasyOCR extracts text from the cropped images
3. **Text Cleaning**: Custom algorithms in `cleantext.py` parse player names and power levels
4. **Data Validation**: Identifies suspicious entries based on power thresholds and text patterns
5. **Deduplication**: Combines results from multiple images, keeping the highest power for each player

## Project Structure

```
├── app.py              # Main Streamlit application
├── cleantext.py        # OCR text processing and cleaning logic
├── ocr.py             # Alternative OCR processing (legacy)
├── crop.sh            # Shell script for image cropping
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .gitignore         # Git ignore rules for sensitive data
└── README.md          # This file
```

**Note**: This repository does not contain sample screenshots or sensitive game data. Users should provide their own screenshots from Metal Slug Awakening for processing.

## Configuration

You can adjust the OCR processing behavior by modifying constants in `cleantext.py`:

- `MIN_DIGITS`: Minimum digits required for a valid power level (default: 6)
- `STRICT_MIN_POWER`: Minimum power threshold (default: 3,000,000)
- `DROP_TOKENS`: Words to ignore during name extraction

## Troubleshooting

### ImageMagick Issues
- Ensure ImageMagick is installed and accessible via the `magick` command
- On some systems, you may need to use `convert` instead of `magick`

### OCR Accuracy
- Ensure screenshots are clear and well-lit
- The cropping coordinates are optimized for specific screen resolutions
- Adjust `MIN_CONF` in the OCR settings if needed

### Memory Issues
- EasyOCR requires significant RAM, especially on first run
- Consider using Docker with adequate memory allocation
- GPU acceleration can be enabled by setting `gpu=True` in the OCR reader

## Security & Privacy

This application:
- **Processes images locally** - uploaded screenshots are processed in temporary directories and automatically cleaned up
- **No data retention** - images and extracted data are not stored permanently by the application
- **No network transmission** - all OCR processing happens on your local machine or Docker container
- **Clean repository** - this repository contains no game screenshots or sensitive player data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

**Important**: Do not commit actual game screenshots or player data to the repository. The `.gitignore` file is configured to prevent this, but please be mindful when contributing.

## License

This project is provided as-is for educational and personal use.
