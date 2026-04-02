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

        return jsonify(result)

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