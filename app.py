import os
import gdown
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from ml_api import detector, OIL_SPILL_DECISION_THRESHOLD_PERCENT

# ==============================
# MODEL DOWNLOAD
# ==============================

MODEL_PATH = "model/oil_spill_model.keras"

def download_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs("model", exist_ok=True)

        print("Downloading model...")

        url = "https://drive.google.com/uc?id=1ouzBqPc4uV8QzglzIBS_BtIFczCExXN4"
        gdown.download(url, MODEL_PATH, quiet=False)

        if os.path.exists(MODEL_PATH):
            print("Model downloaded successfully")
        else:
            print("Model download failed")

download_model()

# ==============================
# FLASK APP
# ==============================

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/outputs"

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = detector.predict(filepath)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    return {
        "status": "ok",
        "model_loaded": detector.model_loaded
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)