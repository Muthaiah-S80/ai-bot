# **Project: Error Resolver Bot** 
A chat-style UI that accepts text or screenshots, extracts error text (EasyOCR), searches a knowledge base (ServiceNow & SharePoint mock data), returns a suggested solution with source, and records thumbs-up / thumbs-down feedback.
**Status**: Runs locally (EasyOCR offline); code and architecture ready to use AWS services when access is available.

# **Contents of this README**
```markdown
Quick summary
Repo layout (what files / folders mean)
Prerequisites (local)
Quickstart — run locally (step-by-step)
Testing with Postman & frontend
Feedback database details (SQLite)
How OCR works (EasyOCR local & offline model steps)
Switching to AWS (what “AWS access given” means and exact changes)
Deployment suggestions & security notes
Troubleshooting & common errors
Next steps / extension ideas
```
# **1. Quick summary**
This repository implements a local Error Resolver bot:
Frontend: Chat UI (HTML/CSS/JS) that resembles a ChatGPT-style message stream with avatars and feedback buttons.
Backend: Flask API that accepts text or uploaded image, extracts text (EasyOCR), runs a TF-IDF search against local mock KB (ServiceNow & SharePoint JSON), and returns the best solution + source.
Feedback: thumbs up/down stored to a local SQLite DB for later analysis/retraining.
AWS-ready: code is structured so you can replace local components with AWS services (S3, Textract, Rekognition, Bedrock, DynamoDB) once you have AWS access.

**# 2. Repo layout**
```markdown
error-resolver-bot/
├── backend/
│   ├── app.py                 # Flask app (serves API + frontend)
│   ├── ocr_handler.py         # EasyOCR wrapper
│   ├── resolver.py            # Orchestrates OCR + search
│   ├── search_engine.py       # TF-IDF search implementation
│   ├── feedback_db.py         # SQLite helpers
│   ├── uploads/               # uploaded images (runtime)
│   └── data/
│       ├── servicenow_data.json
│       └── sharepoint_data.json
├── frontend/
│   ├── index.html             # Chat UI
│   ├── style.css
│   └── script.js
├── requirements.txt
├── README.md
└── architecture_aws.md        # Extra file: AWS integration plan
```
If you followed earlier instructions, you also placed model files under:
C:\Users\<you>\.EasyOCR\models\craft_mlt_25k.pth and english_g2.pth (Windows) — or equivalent Linux path.

**# 3. Prerequisites (local)**
Python 3.9+ (3.10 recommended)
pip
Recommended: virtualenv / venv
Packages (installed via requirements.txt): Flask, easyocr, scikit-learn, pillow, numpy, sqlalchemy (or sqlite3 builtin), flask-cors
Example requirements.txt (included):
flask
flask-cors
easyocr
scikit-learn
pillow
numpy
sqlalchemy
Note about EasyOCR:
It downloads models on first run unless you provide offline .pth files. In blocked office networks, put craft_mlt_25k.pth and english_g2.pth into C:\Users\<you>\.EasyOCR\models\ (Windows) or ~/.EasyOCR/models/. See section 7.

# **4. Quickstart — run locally (step-by-step)**
Clone repo:
git clone https://github.com/<your-org>/error-resolver-bot.git
cd error-resolver-bot/backend
Create & activate virtualenv (optional but recommended):
Windows: python -m venv venv venv\Scripts\activate
macOS / Linux: python -m venv venv source venv/bin/activate
Install Python dependencies:
pip install -r ../requirements.txt
 Or if requirements.txt is in backend:
 pip install -r requirements.txt
Place mock KB data if not present:
backend/data/servicenow_data.json
backend/data/sharepoint_data.json (Examples are included in the repo. Ensure correct keys: error, solution, source, optionally id.)
Ensure EasyOCR models are available (offline) or your machine can download them. If offline, place .pth files into:
Windows: C:\Users\<you>\.EasyOCR\models\
Linux/macOS: ~/.EasyOCR/models/
Start Flask:
python app.py
Default: http://127.0.0.1:5000/
Open frontend:
Recommended: use Flask-served frontend at http://127.0.0.1:5000/ (app.py is configured to serve frontend/index.html).
Or open frontend/index.html directly if not served.

# **5. Testing with Postman & frontend**
API: /api/chat
Method: POST
Content-Type: multipart/form-data
Fields:
text (optional) - plain error text
file (optional) - image file (png/jpg)
sources (optional) - CSV string: ServiceNow, SharePoint, or ServiceNow,SharePoint
Example Postman form-data
keytypevalue/exampletexttextNullPointerException in module XfilefileUpload screenshot.pngsourcestextboth or ServiceNow
Response (JSON):
```json
{
  "query_text": "...extracted or typed text...",
  "result": {
    "id": "snw-001",
    "title": "...",
    "solution": "...",
    "source": "ServiceNow",
    "score": 0.72
  },
  "fallback": false
}
```
API: /api/feedback
Method: POST
Content-Type: application/json
Body example:
```json
{
  "query_text": "NullPointerException in module X",
  "result_id": "snw-001",
  "source": "ServiceNow",
  "feedback": "up"
}
Returns { "ok": true }
API: /api/feedbacks
Method: GET
Returns list of stored feedback entries.
```
# **6. Feedback DB (SQLite) — schema & usage**
feedback_db.py manages a local SQLite DB (e.g., feedback.db) with a table feedback:
Schema:
```sql
CREATE TABLE feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  query_text TEXT,
  result_id TEXT,
  source TEXT,
  feedback TEXT, -- 'up' or 'down'
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```
Functions included:
store_feedback(query, result_id, source, feedback) → inserts row
get_all_feedback(limit) → fetch rows for inspection
get_stats() → aggregate thumbs up/down counts
Where used: Frontend’s thumbs up/down triggers /api/feedback to record votes.

# **7. OCR: EasyOCR local & offline model steps**
Normal (online) behavior:
On first easyocr.Reader() call, EasyOCR downloads model weights automatically (may take several minutes).
Cache location: ~/.EasyOCR/models/ (Windows: C:\Users\<you>\.EasyOCR\models\)
Offline / blocked network (office):
Do this on a machine that has Internet access, then copy files to office laptop:
Download these official model files:
craft_mlt_25k.pth (detection)
english_g2.pth (recognition for English) Official releases are linked on EasyOCR GitHub releases.
Place files into:
Windows: C:\Users\<you>\.EasyOCR\models\craft_mlt_25k.pth and english_g2.pth
Linux/macOS: ~/.EasyOCR/models/
If the files you obtained are zipped, extract them. If the downloaded filename is .bin — rename it to .pth (e.g. craft_mlt_25k.bin → craft_mlt_25k.pth). Confirm the files are valid sizes (tens to hundreds of MB).
Test with a short script:
```python
import easyocr
reader = easyocr.Reader(['en'], gpu=False)
print(reader.readtext('path/to/image.png', detail=0, paragraph=True))
```
If EasyOCR still tries to download:
You can force local model load with model_storage_directory argument:
```python
reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=r'C:\Users\<you>\.EasyOCR\models', download_enabled=False)
```

# **8. Switching to AWS — what “AWS access given” means & exact change points**
When your team gives AWS access (IAM user/role and keys), you can replace local components with managed AWS services for production:
What access is required
--> S3: PutObject/List/GetObject (for image uploads and result storage)
--> Textract: textract:DetectDocumentText (or async AnalyzeDocument)
--> Rekognition (optional): rekognition:DetectText or additional image classification
--> Bedrock / SageMaker / OpenAI (if using): permission to call generative model API
--> DynamoDB (or RDS): PutItem / Query for feedback persistence
--> Lambda / ECS / ECR / EC2: optional compute for serverless processing or hosting
--> CloudWatch: logs & monitoring
Files / code to change (exact pointers)
--> OCR (EasyOCR) → AWS Textract Replace ocr_handler.extract_text_from_image() to call Textract (boto3). Textract returns JSON blocks; convert lines into a single query string.
--> Uploads to local /uploads → S3 When a user uploads image, save to S3 (unique key), and optionally trigger Lambda / S3 event to process automatically.
--> AI fallback (local Flan-T5/OpenAI) → AWS Bedrock Replace local inference with Bedrock runtime call (or use OpenAI as before). Keep the wrapper function so switching is one-line.
--> Feedback storage: SQLite → DynamoDB Replace feedback_db.py functions with boto3 DynamoDB calls to PutItem, Query, and Scan.
--> Hosting: run Flask behind a container (Docker) and deploy to ECS/Fargate / EC2 / EKS. Or convert to serverless (API Gateway + Lambda).

Example Textract call (boto3):
```python
import boto3
tex = boto3.client('textract')
with open('path/to/image', 'rb') as f:
    resp = tex.detect_document_text(Document={'Bytes': f.read()})
lines = [b['Text'] for b in resp['Blocks'] if b['BlockType']=='LINE']
query_text = "\n".join(lines)
```
# **9. Deployment suggestions & security**
Do not commit API keys, .env, or model weights to GitHub. Use .gitignore for venv/, uploads/, *.db, and ~/.EasyOCR/models.
Use environment variables for AWS credentials and OpenAI keys in production. For local dev, use aws configure or a .env (not committed).
For production, use HTTPS and secure API endpoints (Cognito / IAM / API Gateway).
Rotate AWS keys and grant least privilege.

# **10. Troubleshooting & common errors**
pytesseract.TesseractNotFoundError
This app uses EasyOCR (no Tesseract required). If older code calls pytesseract, remove or install Tesseract binary and add to PATH.
EasyOCR stuck on "Downloading model"
Office firewall likely blocks downloads. Use offline model installation steps (section 7).
FileNotFoundError: data/servicenow_data.json
Ensure backend/data/servicenow_data.json exists. Prefer absolute or os.path.join(BASE_DIR, 'data', 'servicenow_data.json') in code.
No text found in image
Verify:
The reader initialization prints “Initializing…”
The model files exist in ~/.EasyOCR/models/
The image path is correct (use absolute path for debugging)
Try simpler/clear image (black text on white background)
CORS errors (frontend)
If serving frontend separately, enable CORS in Flask (flask-cors) or serve frontend via Flask to avoid cross-origin issues.

# **11. Next steps & extension ideas**
Replace TF-IDF with SBERT embeddings and FAISS for semantic matches (if you want higher quality at scale). The repo is already designed so you can swap search engine implementations.
Add usage logs and a retraining pipeline that uses feedback to update KB or suggest new KB entries.
Add user authentication and RBAC to restrict who can query sensitive KB entries.
Set up CI/CD: build & test, run static checker, then push container image to ECR.
Add a small admin dashboard to view feedback stats and top failing queries.
Contact / Support
If you encounter any issues while following the steps (EasyOCR model placement, Flask errors, or AWS integration planning), paste the exact terminal output and I will provide the next concrete fix.
Useful commands summary
Create virtualenv & install:
python -m venv venv
# Windows:
venv\Scripts\activate
# mac/linux:
source venv/bin/activate
 
pip install -r requirements.txt
Run Flask:
cd backend
python app.py
# Open http://127.0.0.1:5000/

Postman test (multipart/form-data): POST http://127.0.0.1:5000/api/chat with file and/or text and sources.
