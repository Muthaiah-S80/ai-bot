# resolver.py
import os
from ocr_handler import extract_text_from_image
from search_engine import find_best_match
 
def resolve_from_text_or_image(text_input=None, image_path=None, sources=["ServiceNow","SharePoint"]):
    """
    Main resolver logic: prefer provided text_input; if empty, run OCR on image_path.
    Returns dict: { query_text, result (dict or None), score, fallback }
    """
    query_text = (text_input or "").strip()
    if not query_text and image_path:
        query_text = extract_text_from_image(image_path)
 
    if not query_text:
        return {"query_text": "", "result": None, "score": 0.0, "fallback": True, "message": "No text found in image and no text input provided."}
 
    best_item, score = find_best_match(query_text, sources=sources)
    if best_item:
        return {"query_text": query_text, "result": best_item, "score": score, "fallback": False}
    else:
        # fallback simple response
        fallback_text = f"No close match found in selected sources. Extracted: {query_text}"
        return {"query_text": query_text, "result": {"id": None, "title": None, "solution": fallback_text, "source": "AI-Fallback"}, "score": score, "fallback": True}