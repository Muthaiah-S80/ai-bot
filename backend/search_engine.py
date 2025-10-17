# search_engine.py
import os, json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SN_PATH = os.path.join(BASE_DIR, "data", "servicenow_data.json")
SP_PATH = os.path.join(BASE_DIR, "data", "sharepoint_data.json")
 
def load_all_data():
    data = []
    if os.path.exists(SN_PATH):
        with open(SN_PATH, "r", encoding="utf-8") as f:
            data += json.load(f)
    if os.path.exists(SP_PATH):
        with open(SP_PATH, "r", encoding="utf-8") as f:
            data += json.load(f)
    return data
 
def load_data_by_source(sources):
    data = []
    if "ServiceNow" in sources and os.path.exists(SN_PATH):
        with open(SN_PATH, "r", encoding="utf-8") as f:
            data += json.load(f)
    if "SharePoint" in sources and os.path.exists(SP_PATH):
        with open(SP_PATH, "r", encoding="utf-8") as f:
            data += json.load(f)
    return data
 
def find_best_match(query, sources=["ServiceNow","SharePoint"], threshold=0.15):
    """
    Returns tuple (best_item_dict, score) or (None, 0.0) if none above threshold.
    Each data item expected to have keys: id, error_text, solution, source, title (optional)
    """
    data = load_data_by_source(sources)
    if not data:
        return None, 0.0
 
    texts = [d.get("error_text", d.get("text", d.get("error",""))) for d in data]
    # build TF-IDF with texts + query
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform(texts + [query])
    except ValueError:
        return None, 0.0
 
    q_vec = tfidf[-1]
    corpus = tfidf[:-1]
    sim = cosine_similarity(q_vec, corpus)[0]
    best_idx = sim.argmax()
    best_score = float(sim[best_idx])
    if best_score < threshold:
        return None, best_score
    return data[best_idx], best_score