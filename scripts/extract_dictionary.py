"""
Script to extract dictionary from PDF using OCR.

Requirements:
- Tesseract OCR installed (with Russian language pack)
- Poppler installed (for pdf2image)

Installation on Windows:
1. Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
   - Install with Russian language pack
   - Add to PATH or set TESSERACT_CMD below

2. Poppler: https://github.com/oschwartz10612/poppler-windows/releases
   - Extract and add 'bin' folder to PATH or set POPPLER_PATH below
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Tuple, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install pdf2image pytesseract Pillow")
    sys.exit(1)


# Configuration
POPPLER_PATH = None  # Set if not in PATH, e.g., r"C:\poppler\bin"
TESSERACT_CMD = None  # Set if not in PATH, e.g., r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Paths
CONTENT_DIR = Path(__file__).parent.parent / "content"
OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "data"
DICTIONARY_PDF = CONTENT_DIR / "Табасаранско-русский словарь.pdf"


def setup_tesseract():
    """Configure Tesseract path"""
    if TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

    # Test Tesseract
    try:
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {version}")
    except Exception as e:
        print(f"Tesseract not found: {e}")
        print("Please install Tesseract OCR with Russian language pack")
        sys.exit(1)


def pdf_to_images(pdf_path: Path, dpi: int = 400) -> List[Image.Image]:
    """Convert PDF pages to images"""
    print(f"Converting PDF to images (DPI={dpi})...")

    kwargs = {"dpi": dpi}
    if POPPLER_PATH:
        kwargs["poppler_path"] = POPPLER_PATH

    try:
        images = convert_from_path(str(pdf_path), **kwargs)
        print(f"Converted {len(images)} pages")
        return images
    except Exception as e:
        print(f"Error converting PDF: {e}")
        print("Make sure Poppler is installed and in PATH")
        sys.exit(1)


def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess image for better OCR"""
    # Convert to grayscale
    gray = image.convert('L')

    # Simple thresholding for better contrast
    threshold = 180
    binary = gray.point(lambda x: 255 if x > threshold else 0, '1')

    return binary


def ocr_image(image: Image.Image, lang: str = "rus") -> str:
    """Run OCR on image"""
    # OCR configuration
    config = r'--oem 3 --psm 6'  # LSTM engine, assume uniform block of text

    text = pytesseract.image_to_string(image, lang=lang, config=config)
    return text


def extract_dictionary_entries(text: str) -> List[dict]:
    """
    Parse OCR text to extract dictionary entries.

    Typical dictionary format:
    ТАБАСАРАНСКОЕ_СЛОВО — русский перевод; другое значение
    """
    entries = []

    # Split into lines
    lines = text.split('\n')

    current_entry = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to match dictionary entry pattern
        # Pattern: word followed by dash and translation
        match = re.match(r'^([А-Яа-яӀ]+)\s*[—–-]\s*(.+)$', line)

        if match:
            # Save previous entry
            if current_entry:
                entries.append(current_entry)

            word = match.group(1).strip()
            translation = match.group(2).strip()

            # Parse translations (separated by ;)
            translations = [t.strip() for t in translation.split(';') if t.strip()]

            current_entry = {
                'word': word,
                'translations': translations,
                'raw_line': line
            }
        elif current_entry and line:
            # Continuation of previous entry
            current_entry['translations'].extend(
                [t.strip() for t in line.split(';') if t.strip()]
            )

    # Don't forget last entry
    if current_entry:
        entries.append(current_entry)

    return entries


def save_entries(entries: List[dict], output_path: Path):
    """Save extracted entries to JSON"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(entries)} entries to {output_path}")


def process_single_page(image: Image.Image, page_num: int) -> List[dict]:
    """Process a single page"""
    print(f"Processing page {page_num}...")

    # Preprocess
    processed = preprocess_image(image)

    # OCR
    text = ocr_image(processed)

    # Extract entries
    entries = extract_dictionary_entries(text)

    print(f"  Found {len(entries)} entries")
    return entries


def main():
    """Main extraction process"""
    print("=" * 60)
    print("Tabasaran Dictionary Extractor")
    print("=" * 60)

    # Setup
    setup_tesseract()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Check PDF exists
    if not DICTIONARY_PDF.exists():
        print(f"Dictionary PDF not found: {DICTIONARY_PDF}")
        sys.exit(1)

    # Convert to images
    images = pdf_to_images(DICTIONARY_PDF)

    # Process each page
    all_entries = []
    for i, image in enumerate(images, 1):
        entries = process_single_page(image, i)
        all_entries.extend(entries)

        # Save intermediate results every 50 pages
        if i % 50 == 0:
            save_entries(all_entries, OUTPUT_DIR / f"dictionary_partial_{i}.json")

    # Save final result
    save_entries(all_entries, OUTPUT_DIR / "dictionary_raw.json")

    print("=" * 60)
    print(f"Extraction complete!")
    print(f"Total entries: {len(all_entries)}")
    print(f"Output: {OUTPUT_DIR / 'dictionary_raw.json'}")


def test_ocr_single_page(page_num: int = 10):
    """Test OCR on a single page for debugging"""
    print(f"Testing OCR on page {page_num}...")

    setup_tesseract()

    images = pdf_to_images(DICTIONARY_PDF)

    if page_num > len(images):
        print(f"Only {len(images)} pages in PDF")
        return

    image = images[page_num - 1]
    processed = preprocess_image(image)

    # Save processed image for inspection
    processed.save(OUTPUT_DIR / f"test_page_{page_num}.png")
    print(f"Saved processed image to {OUTPUT_DIR / f'test_page_{page_num}.png'}")

    # Run OCR
    text = ocr_image(processed)

    # Save OCR result
    with open(OUTPUT_DIR / f"test_page_{page_num}.txt", 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Saved OCR result to {OUTPUT_DIR / f'test_page_{page_num}.txt'}")

    # Show first 1000 chars
    print("\nOCR Result (first 1000 chars):")
    print("-" * 40)
    print(text[:1000])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract dictionary from PDF")
    parser.add_argument("--test", type=int, help="Test OCR on single page number")
    parser.add_argument("--full", action="store_true", help="Run full extraction")

    args = parser.parse_args()

    if args.test:
        test_ocr_single_page(args.test)
    elif args.full:
        main()
    else:
        print("Usage:")
        print("  python extract_dictionary.py --test 10  # Test on page 10")
        print("  python extract_dictionary.py --full     # Full extraction")
