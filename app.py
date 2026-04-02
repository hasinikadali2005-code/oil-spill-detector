import os
import gdown
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path

# ==============================
# 🔥 SAFE IMPORT (IMPORTANT)
# ==============================
try:
    from ml_api import detector, OIL_SPILL_DECISION_THRESHOLD_PERCENT
    MODEL_AVAILABLE = True
except Exception as e:
    print("ML not available:", e)
    MODEL_AVAILABLE = False

# ==============================
# 🔥 MODEL DOWNLOAD
# ==============================

MODEL_PATH = "model/oil_spill_model.keras"

def download_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs("model", exist_ok=True)
        print("Downloading model...")

        url = "https://drive.google.com/uc?id=1ouzBqPc4uV8QzglzIBS_BtIFczCExXN4"
        gdown.download(url, MODEL_PATH, quiet=False)

        print("Model downloaded!")

# Download only if ML exists
if MODEL_AVAILABLE:
    download_model()

# ==============================
# 🚀 FLASK APP
# ==============================

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'outputs')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 20 * 1024 * 1024

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if not MODEL_AVAILABLE:
        return jsonify({
            "error": "ML model not available in deployment (free tier limitation)"
        }), 500

    try:
        file = request.files.get('file')

        if not file:
            return jsonify({'error': 'No file uploaded'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = detector.predict(filepath)

        confidence = float(result.get('confidence', 0.0))
        has_oil_spill = confidence >= OIL_SPILL_DECISION_THRESHOLD_PERCENT

        return jsonify({
            'success': True,
            'confidence': confidence,
            'has_oil_spill': has_oil_spill,
            'status_text': 'Oil Spill Detected' if has_oil_spill else 'Not Detected'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    return jsonify({
        "status": "running",
        "ml_loaded": MODEL_AVAILABLE
    })


# ==============================
# 🔥 RENDER FIX
# ==============================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)