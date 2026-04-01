import os
import gdown

"""
Oil Spill Detection Web Application
Flask-based UI backend for oil spill detection
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from ml_api import detector, OIL_SPILL_DECISION_THRESHOLD_PERCENT
from pathlib import Path

# ==============================
# 🔥 MODEL DOWNLOAD (ADDED)
# ==============================

MODEL_PATH = "model/oil_spill_model.keras"

def download_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs("model", exist_ok=True)

        print("Downloading model from Google Drive...")

        url = "https://drive.google.com/uc?id=1ouzBqPc4uV8QzglzIBS_BtIFczCExXN4"
        gdown.download(url, MODEL_PATH, quiet=False)

        print("Model downloaded successfully!")

download_model()

# ==============================
# 🚀 FLASK APP
# ==============================

# Flask app configuration
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'outputs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# Ensure folders exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """
    Check if file has allowed extension
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """
    Render the main page
    """
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    Handle image upload and prediction
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Allowed: PNG, JPG, JPEG, BMP, GIF'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = detector.predict(filepath)

        if 'error' in result:
            return jsonify(result), 400

        confidence = float(result.get('confidence', 0.0))

        has_oil_spill_result = result.get('has_oil_spill', result.get('is_oil_spill'))
        if has_oil_spill_result is None:
            has_oil_spill = confidence >= OIL_SPILL_DECISION_THRESHOLD_PERCENT
        else:
            has_oil_spill = bool(has_oil_spill_result)

        original_image_base64 = result.get('original_image')
        mask_image_base64 = result.get('mask_image')
        overlay_image_base64 = result.get('overlay_image')

        original_image = f"data:image/png;base64,{original_image_base64}" if original_image_base64 else None
        mask_image = f"data:image/png;base64,{mask_image_base64}" if mask_image_base64 else None
        overlay_image = f"data:image/png;base64,{overlay_image_base64}" if overlay_image_base64 else None

        response = {
            'success': bool(result.get('success', True)),
            'confidence': confidence,
            'has_oil_spill': has_oil_spill,
            'is_oil_spill': has_oil_spill,
            'status_text': 'Oil Spill Detected' if has_oil_spill else 'Not Detected',
            'original_image': original_image,
            'mask_image': mask_image,
            'overlay_image': overlay_image
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector.model_loaded
    }), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum size: 20MB'}), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ==============================
# 🔥 RENDER FIX (UPDATED)
# ==============================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)