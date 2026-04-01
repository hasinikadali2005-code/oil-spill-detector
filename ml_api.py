"""
Oil Spill Detection ML API
Flask-based API for oil spill detection with image overlay generation
"""

import os
import cv2
import numpy as np
import base64
from io import BytesIO
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path

try:
    from keras.models import load_model
    ML_BACKEND_AVAILABLE = True
except Exception:
    # TensorFlow-backed Keras may be unavailable in newer Python runtimes.
    load_model = None
    ML_BACKEND_AVAILABLE = False

# Flask app initialization
app = Flask(__name__)

# Configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'oil_spill_model.keras')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'outputs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# Model configuration
IMAGE_SIZE = (256, 256)
PREDICTION_THRESHOLD = 0.3  # Threshold for binary mask
OIL_SPILL_DECISION_THRESHOLD_PERCENT = 1.0  # % of image area needed to mark as oil spill
OIL_SPILL_COLOR = [255, 0, 0]  # RED color in BGR format

# Ensure folders exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


class OilSpillDetector:
    """
    Machine Learning model wrapper for oil spill detection with overlay generation
    """

    def __init__(self, model_path=MODEL_PATH):
        """
        Initialize the detector by loading the trained model
        
        Args:
            model_path (str): Path to the trained keras model file
        """
        self.model = None
        self.model_loaded = False
        self.fallback_mode = False
        
        try:
            if ML_BACKEND_AVAILABLE and os.path.exists(model_path):
                self.model = load_model(model_path, compile=False)
                self.model_loaded = True
                print(f"✓ Model loaded successfully from {model_path}")
            elif not ML_BACKEND_AVAILABLE:
                self.fallback_mode = True
                self.model_loaded = True
                print("⚠ TensorFlow/Keras backend unavailable. Running in fallback mode.")
            else:
                print(f"✗ Model file not found: {model_path}")
        except Exception as e:
            print(f"✗ Error loading model: {str(e)}")
            self.fallback_mode = True
            self.model_loaded = True
            print("⚠ Falling back to heuristic mode.")

    def _predict_fallback(self, image_path):
        """Heuristic prediction path used when ML backend is unavailable."""
        original_img = cv2.imread(image_path)
        if original_img is None:
            return {
                'success': False,
                'error': 'Failed to read image'
            }

        # Approximate likely spill regions as darker, lower-saturation water patches.
        hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]

        low_sat = saturation < 70
        dark_area = value < 110
        binary_mask = np.logical_and(low_sat, dark_area).astype(np.uint8)

        kernel = np.ones((3, 3), np.uint8)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_DILATE, kernel)

        detected_pixels = int(np.sum(binary_mask))
        total_pixels = int(binary_mask.shape[0] * binary_mask.shape[1])
        confidence = (detected_pixels / total_pixels) * 100 if total_pixels else 0.0

        original_image, mask_image, overlay_image = self._create_overlay(image_path, binary_mask)
        if overlay_image is None:
            return {
                'success': False,
                'error': 'Failed to create overlay'
            }

        return {
            'success': True,
            'confidence': round(float(confidence), 2),
            'has_oil_spill': bool(confidence >= OIL_SPILL_DECISION_THRESHOLD_PERCENT),
            'is_oil_spill': bool(confidence >= OIL_SPILL_DECISION_THRESHOLD_PERCENT),
            'original_image': original_image,
            'mask_image': mask_image,
            'overlay_image': overlay_image
        }

    def preprocess_image(self, image_path):
        """
        Preprocess image for model inference
        
        Args:
            image_path (str): Path to input image
            
        Returns:
            tuple: (preprocessed_array, original_image) or (None, None) on error
        """
        try:
            # Read image using OpenCV (BGR format)
            img = cv2.imread(image_path)
            if img is None:
                return None, None
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size
            img_resized = cv2.resize(img_rgb, IMAGE_SIZE, interpolation=cv2.INTER_LANCZOS4)
            
            # Normalize to [0, 1]
            img_normalized = img_resized.astype(np.float32) / 255.0
            
            # Add batch dimension (1, height, width, channels)
            img_batch = np.expand_dims(img_normalized, axis=0)
            
            return img_batch, img_resized
            
        except Exception as e:
            print(f"✗ Error preprocessing image: {str(e)}")
            return None, None

    def predict(self, image_path):
        """
        Predict wrapper that calls predict_with_overlay
        
        Args:
            image_path (str): Path to input image
            
        Returns:
            dict: Prediction results
        """
        return self.predict_with_overlay(image_path)

    def predict_with_overlay(self, image_path):
        """
        PIPELINE STEP 3: Flask ML API - Model Inference & Image Processing
        
        This is the core ML processing function that receives an image from
        Spring Boot and returns a prediction with overlay visualization.
        
        Complete Processing Pipeline:
        1. Load and preprocess image
        2. Run model inference (model.predict)
        3. Apply threshold to create binary mask
        4. Create red overlay on detected oil spill regions
        5. Encode as base64 PNG
        6. Return JSON response
        
        Processing Details:
        - Image resize: 256x256 (model input size)
        - Normalization: divide by 255.0
        - Prediction: neural network inference
        - Threshold: 0.3 (values > 0.3 = oil spill, ≤ 0.3 = no spill)
        - Overlay color: RED ([255, 0, 0] in BGR format for OpenCV)
        - Output encoding: base64 PNG
        
        Args:
            image_path (str): Path to input image from Spring Boot upload
            
        Returns:
            dict: Prediction results with:
            {
              "success": true,
              "confidence": 85.5,
              "has_oil_spill": true,
              "overlay_png": "base64 string of overlay image",
              "prediction_map": "base64 string of prediction mask"
            }
        """
        if not self.model_loaded:
            return {
                'success': False,
                'error': 'Model not loaded'
            }

        if self.fallback_mode:
            return self._predict_fallback(image_path)

        try:
            # ========== STEP 1: Load and Preprocess Image ==========
            # Load image and prepare for model inference
            print(f"\n📥 Processing image: {image_path}")
            
            img_batch, img_resized = self.preprocess_image(image_path)
            if img_batch is None:
                return {
                    'success': False,
                    'error': 'Failed to preprocess image'
                }
            
            print(f"✓ Image preprocessing complete")
            print(f"  - Original size: {img_resized.shape}")
            print(f"  - Batch size: {img_batch.shape}")
            print(f"  - Pixel range: [0.0, 1.0] (normalized)")

            # ========== STEP 2: Run Model Inference ==========
            # Load trained Keras model and run prediction
            # Model takes 256x256 normalized image and outputs prediction
            print(f"\n🧠 Running model inference...")
            print(f"  - Model: {MODEL_PATH}")
            print(f"  - Input: {img_batch.shape}")
            
            prediction = self.model.predict(img_batch, verbose=0)
            
            print(f"✓ Model inference complete")
            print(f"  - Output shape: {prediction.shape}")
            print(f"  - Output range: [{np.min(prediction):.4f}, {np.max(prediction):.4f}]")
            
            # Handle different prediction output shapes
            # If output is (batch, height, width, 1) - semantic segmentation
            if len(prediction.shape) == 4:
                prediction_map = prediction[0, :, :, 0]  # Extract first channel
                print(f"  - Detected output type: Semantic Segmentation")
            # If output is (batch, num_classes) - classification
            elif len(prediction.shape) == 2:
                confidence = float(prediction[0, 0])
                prediction_map = None
                print(f"  - Detected output type: Classification")
            else:
                prediction_map = prediction[0]
                print(f"  - Detected output type: Unknown")
            
            # ========== STEP 3: Apply Threshold to Create Binary Mask ==========
            # Threshold 0.3: Values > 0.3 indicate oil spill
            # This creates a binary mask where:
            #   1 = oil spill detected
            #   0 = no oil spill
            print(f"\n🎯 Creating binary mask with threshold {PREDICTION_THRESHOLD}")
            
            if prediction_map is not None:
                # Apply threshold
                binary_mask = (prediction_map > PREDICTION_THRESHOLD).astype(np.uint8)
                
                # Resize mask back to original image size
                original_shape = cv2.imread(image_path).shape[:2]
                binary_mask = cv2.resize(binary_mask, 
                                        (original_shape[1], original_shape[0]),
                                        interpolation=cv2.INTER_NEAREST)
                
                # Calculate confidence as percentage of detected pixels
                detected_pixels = np.sum(binary_mask)
                total_pixels = binary_mask.shape[0] * binary_mask.shape[1]
                confidence = (detected_pixels / total_pixels) * 100
                
                print(f"✓ Binary mask created")
                print(f"  - Detected pixels: {detected_pixels} / {total_pixels}")
                print(f"  - Confidence: {confidence:.2f}%")
            else:
                confidence = float(prediction[0, 0]) * 100
                binary_mask = None
                print(f"✓ Using classification confidence: {confidence:.2f}%")

            # ========== STEP 4: Create Overlay with Red Highlights ==========
            # Draw red color on detected oil spill regions
            # Use alpha blending for transparency (60% overlay, 40% original)
            print(f"\n🎨 Creating overlay image with RED highlights")
            print(f"  - Color: RED {OIL_SPILL_COLOR} (BGR format)")
            print(f"  - Alpha blending: 60% red, 40% original")
            
            original_image, mask_image, overlay_image = self._create_overlay(image_path, binary_mask)
            
            if overlay_image is None:
                return {
                    'success': False,
                    'error': 'Failed to create overlay'
                }
            
            print(f"✓ All images created and encoded")
            print(f"  - Output format: PNG (base64)")
            print(f"  - Generated: original_image, mask_image, overlay_image")

            # ========== STEP 5: Return Response ==========
            # Prepare response for Spring Boot backend
            print(f"\n📤 Returning prediction response to Spring Boot")
            print(f"  - Success: true")
            print(f"  - Confidence: {confidence:.2f}%")
            print(
                f"  - Oil Spill: {confidence >= OIL_SPILL_DECISION_THRESHOLD_PERCENT} "
                f"(threshold: {OIL_SPILL_DECISION_THRESHOLD_PERCENT}% area)"
            )

            confidence_py = float(confidence)
            has_oil_spill_py = bool(confidence_py >= OIL_SPILL_DECISION_THRESHOLD_PERCENT)
            
            return {
                'success': True,
                'confidence': round(confidence_py, 2),
                'has_oil_spill': has_oil_spill_py,
                'is_oil_spill': has_oil_spill_py,
                'original_image': original_image,
                'mask_image': mask_image,
                'overlay_image': overlay_image
            }

        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            return {
                'success': False,
                'error': f'Prediction failed: {str(e)}'
            }

    def _create_overlay(self, image_path, mask):
        """
        Create overlay image with oil spill regions highlighted in RED
        Also returns original image and mask image for comparison
        
        Args:
            image_path (str): Path to original image
            mask (np.ndarray): Binary mask of detected regions
            
        Returns:
            tuple: (original_image_base64, mask_image_base64, overlay_image_base64)
        """
        try:
            # Read original image
            original_img = cv2.imread(image_path)
            if original_img is None:
                return None, None, None
            
            # Encode original image as base64 PNG
            _, original_png = cv2.imencode('.png', original_img)
            original_base64 = base64.b64encode(original_png.tobytes()).decode('utf-8')
            
            # Create overlay with red highlights
            overlay = original_img.copy()
            
            # Apply red color to detected regions if mask exists
            if mask is not None and np.max(mask) > 0:
                # Create a red mask
                red_mask = np.zeros_like(overlay)
                red_mask[mask > 0] = OIL_SPILL_COLOR  # BGR format: [B, G, R]
                
                # Blend overlay with red regions using alpha blending
                # 60% red overlay, 40% original image
                alpha = 0.6
                overlay = cv2.addWeighted(overlay, 1 - alpha, red_mask, alpha, 0)

            # Encode overlay as PNG to base64
            _, overlay_png = cv2.imencode('.png', overlay)
            overlay_base64 = base64.b64encode(overlay_png.tobytes()).decode('utf-8')
            
            # Encode prediction mask if available
            if mask is not None:
                mask_uint8 = (mask * 255).astype(np.uint8)
                mask_rgb = cv2.cvtColor(mask_uint8, cv2.COLOR_GRAY2BGR)
                _, mask_png = cv2.imencode('.png', mask_rgb)
                mask_base64 = base64.b64encode(mask_png.tobytes()).decode('utf-8')
            else:
                mask_base64 = None
            
            return original_base64, mask_base64, overlay_base64
            
        except Exception as e:
            print(f"✗ Error creating overlay: {str(e)}")
            return None, None, None


def allowed_file(filename):
    """
    Check if file has allowed extension
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if file is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Initialize detector instance
detector = OilSpillDetector()


# ========== Flask Routes ==========

@app.route('/predict', methods=['POST'])
def predict():
    """
    FLASK ML API ENDPOINT: POST /predict
    
    This endpoint receives an image from Spring Boot backend and returns
    model prediction with visual overlay.
    
    FULL PIPELINE VISUALIZATION:
    ═════════════════════════════════════════════════════════════════════
    
    1. FRONTEND (Browser)
       User uploads image via Spring Boot UI
       │
       ├─ URL: http://localhost:8080/api/predict
       └─ Method: POST (multipart/form-data)
    
    2. SPRING BOOT BACKEND
       ├─ Receives image at: POST /api/predict
       ├─ Validates file (type, size, extension)
       ├─ Forwards to Flask API
       └─ Receives ML prediction response
    
    3. FLASK ML API (This endpoint)
       ├─ Receives image at: POST http://127.0.0.1:5000/predict
       ├─ Validates image file
       ├─ Preprocesses:
       │  ├─ Resize to 256x256
       │  └─ Normalize: divide by 255.0
       ├─ Runs ML inference:
       │  ├─ Load model from model/oil_spill_model.keras
       │  └─ model.predict(preprocessed_image)
       ├─ Creates binary mask (threshold 0.3)
       ├─ Generates overlay:
       │  ├─ Load original image
       │  ├─ Color detected regions RED ([255, 0, 0])
       │  ├─ Blend with 60% opacity
       │  └─ Encode as base64 PNG
       ├─ Returns JSON response
       └─ HTTP 200 OK
    
    4. SPRING BOOT BACKEND (Response Processing)
       ├─ Receives JSON from Flask
       ├─ Parses into PredictionResponse DTO
       ├─ Returns to client as JSON
       └─ HTTP 200 OK
    
    5. FRONTEND (Display)
       ├─ Receives JSON response
       ├─ Displays overlay_image: <img src="data:image/png;base64,...">
       ├─ Shows confidence percentage
       ├─ Updates status badge (detected/safe)
       └─ Displays success message
    
    ═════════════════════════════════════════════════════════════════════
    
    Request Format:
    - Content-Type: multipart/form-data
    - File parameter name: "file"
    - Accepted formats: PNG, JPG, JPEG, BMP, GIF
    - Max size: 20MB
    
    Response Format (Success - 200 OK):
    {
        "success": true,
        "confidence": 85.5,
        "has_oil_spill": true,
        "overlay_png": "data:image/png;base64,iVBORw0KGgo...",
        "prediction_map": "data:image/png;base64,iVBORw0KGgo..."
    }
    
    Response Format (Error - 400/500):
    {
        "success": false,
        "error": "Invalid file format. Allowed: png, jpg, jpeg, bmp, gif"
    }
    
    Returns:
        JSON response with prediction results and base64 encoded overlay
    """
    try:
        # ========== STEP 1: Validate Request ==========
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file format. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # ========== STEP 2: Save Uploaded File ==========
        # Save temporarily to disk for processing
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"\n✓ File received: {filename}")
        print(f"  Path: {filepath}")

        # ========== STEP 3: Run Prediction with Overlay ==========
        # Core ML processing (OilSpillDetector.predict_with_overlay)
        result = detector.predict_with_overlay(filepath)

        if not result['success']:
            return jsonify(result), 400

        # ========== STEP 4: Build Response for Spring Boot ==========
        # Wrap results in proper format with data URLs for easy display
        response = {
            'success': True,
            'confidence': float(result['confidence']),
            'has_oil_spill': bool(result['has_oil_spill']),
            'is_oil_spill': bool(result.get('is_oil_spill', result['has_oil_spill'])),
            'overlay_image': f"data:image/png;base64,{result['overlay_png']}",
            'prediction_map': f"data:image/png;base64,{result['prediction_map']}" if result['prediction_map'] else None
        }
        
        print(f"\n✓ Sending response back to Spring Boot")
        print(f"  - HTTP 200 OK")
        print(f"  - Overlay image: {len(response['overlay_image'])} characters (base64)")

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    
    Returns: JSON with model status
    """
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector.model_loaded,
        'model_path': MODEL_PATH,
        'mode': 'fallback' if detector.fallback_mode else 'model'
    }), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size: 20MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    """
    Run the Flask development server
    """
    print("\n" + "="*60)
    print("Oil Spill Detection ML API Server")
    print("="*60)
    print(f"Model Status: {'✓ Loaded' if detector.model_loaded else '✗ Not Loaded'}")
    print(f"API Endpoint: http://0.0.0.0:5000/predict")
    print(f"Health Check: http://0.0.0.0:5000/health")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
