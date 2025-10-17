import os
try:
    import easyocr
except Exception as e:
    print("EasyOCR import failed:", e)
    easyocr = None
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
 
_reader = None
def _get_reader():
    global _reader
    if _reader is None:
        if easyocr is None:
            raise RuntimeError("EasyOCR not available. Install easyocr and torch.")
        print("Initializing EasyOCR reader...")
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader
 
def extract_text_from_image(image_path):
    """
    Returns extracted text (or error message).
    """
    try:
        if not os.path.exists(image_path):
            return "File not found."
 
        reader = _get_reader()
        results = reader.readtext(image_path, detail=0, paragraph=True)
 
        if not results:
            return "No text found in image."
 
        return " ".join(results).strip()
 
    except Exception as e:
        return f"OCR Error: {str(e)}"