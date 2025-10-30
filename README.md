# EXIF Metadata Reader

A Flet-based Python application for reading and displaying EXIF metadata from images. This application provides an intuitive file picker interface to view detailed metadata from various image formats, including 16-bit TIFF images.

## Features

- **Simple file picker button** for easy image loading
- **Side-by-side layout** showing image preview and metadata
- **Comprehensive metadata extraction** from multiple sources:
  - PIL EXIF data
  - piexif data (especially useful for TIFF files)
  - Image info metadata
- **Smart filtering** - only displays meaningful metadata that's actually present
- **Support for multiple formats**:
  - JPEG
  - PNG
  - TIFF (including 16-bit)
  - BMP
  - GIF
  - WebP
- **GPS data handling** with proper tag decoding
- **User-friendly display** with formatted values and readable presentation

## Installation

1. Clone this repository or download the files

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. The application window will open with a placeholder on the left and a "Choose Image File" button

3. Click the **"Choose Image File"** button to open a file picker dialog and select an image

4. Once an image is loaded:
   - The **left side** shows the image preview
   - The **right side** displays all available metadata in an organized, scrollable list
   - File information (name, size, format, mode, dimensions) appears at the top of the metadata section
   - Click the button again to load a different image

## Supported Metadata

The application extracts and displays various types of metadata including:

- **EXIF data**: Camera settings, date/time, exposure, ISO, focal length, etc.
- **GPS data**: Location information if available
- **Image properties**: Dimensions, color mode, format, DPI, etc.
- **TIFF tags**: Specific metadata for TIFF files including 16-bit images
- **Custom metadata**: Any additional metadata stored in the image file

Only metadata with actual values is displayed - empty or meaningless fields are automatically filtered out.

## Technical Details

- Built with [Flet](https://flet.dev) for the UI framework
- Uses [Pillow (PIL)](https://pillow.readthedocs.io/) for image handling
- Uses [piexif](https://pypi.org/project/piexif/) for comprehensive EXIF extraction
- Handles 16-bit TIFF images with proper conversion for display
- Gracefully handles various image modes (RGBA, LA, P, I;16, etc.)

## Requirements

- Python 3.7+
- flet >= 0.24.0
- Pillow >= 10.0.0
- piexif >= 1.1.3

## License

This project is open source and available for use and modification.
