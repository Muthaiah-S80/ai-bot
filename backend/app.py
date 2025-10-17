# app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from resolver import resolve_from_text_or_image
import feedback_db
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
os.makedirs(UPLOAD_DIR, exist_ok=True)
 
ALLOWED_EXT = {"png","jpg","jpeg","bmp","tiff"}
 
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/")
CORS(app)
 
def allowed_file(fn):
    return "." in fn and fn.rsplit(".",1)[1].lower() in ALLOWED_EXT
 
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")
 
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Accepts form-data:
    - text : optional typed query
    - file : optional image
    - sources: CSV like "ServiceNow,SharePoint" (optional)
    """
    sources_raw = request.form.get("sources", "ServiceNow,SharePoint")
    sources = [s.strip() for s in sources_raw.split(",") if s.strip()]
    text_input = request.form.get("text", "").strip()
 
    image_path = None
    if "file" in request.files and request.files["file"].filename != "":
        f = request.files["file"]
        if not allowed_file(f.filename):
            return jsonify({"error":"file type not allowed"}), 400
        filename = secure_filename(f.filename)
        save_path = os.path.join(UPLOAD_DIR, filename)
        f.save(save_path)
        image_path = save_path
 
    res = resolve_from_text_or_image(text_input if text_input else None, image_path, sources=sources)
    return jsonify(res)
 
@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    """
    JSON body:
    { query_text, result_id, source, feedback }  feedback = "up"|"down"
    """
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error":"no data"}), 400
    q = data.get("query_text","")
    rid = data.get("result_id", None)
    src = data.get("source", None)
    fb = data.get("feedback", None)
    if fb not in ("up","down"):
        return jsonify({"error":"feedback must be 'up' or 'down'"}), 400
    feedback_db.store_feedback(q, rid, src, fb)
    return jsonify({"ok":True})
 
@app.route("/api/feedbacks", methods=["GET"])
def api_feedbacks():
    rows = feedback_db.get_all_feedback(200)
    # map to dict
    items = [{"id":r[0],"query_text":r[1],"result_id":r[2],"source":r[3],"feedback":r[4],"created_at":r[5]} for r in rows]
    return jsonify(items)
 
if __name__ == "__main__":
    app.run(debug=True, port=5000)