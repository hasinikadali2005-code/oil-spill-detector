import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from ml_api import detector

# ==============================
# FLASK APP
# ==============================

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def as_data_uri(image_value):
    if not image_value:
        return None
    if isinstance(image_value, str) and image_value.startswith('data:image'):
        return image_value
    return f"data:image/png;base64,{image_value}"

# ==============================
# ROUTES
# ==============================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'})

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'})

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'})

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = detector.predict(filepath)
        if not result.get('success', False):
            return jsonify(result), 400

        confidence = float(result.get('confidence', 0.0))
        has_oil_spill = bool(result.get('has_oil_spill', confidence >= 50.0))

        response = {
            'success': True,
            'confidence': round(confidence, 2),
            'has_oil_spill': has_oil_spill,
            'is_oil_spill': has_oil_spill,
            'status_text': 'Oil Spill Detected' if has_oil_spill else 'No Spill',
            'original_image': as_data_uri(result.get('original_image')),
            'mask_image': as_data_uri(result.get('mask_image')),
            'overlay_image': as_data_uri(result.get('overlay_image')),
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    return {
        "status": "ok",
        "model_loaded": detector.model_loaded
    }

# ==============================
# RUN
# ==============================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)