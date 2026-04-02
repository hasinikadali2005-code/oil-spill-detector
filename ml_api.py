import os
import cv2
import numpy as np
import base64
from tensorflow.keras.models import load_model

OIL_SPILL_DECISION_THRESHOLD_PERCENT = 50

class Detector:
    def __init__(self):
        self.model_loaded = False
        self.model = None

        try:
            model_path = "model/oil_spill_model.keras"

            if os.path.exists(model_path):
                self.model = load_model(model_path)
                self.model_loaded = True
                print("✅ Model loaded successfully")
            else:
                print("❌ Model not found")

        except Exception as e:
            print("❌ Model loading error:", e)

    def preprocess(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.resize(img, (256, 256))
        img = img / 255.0
        return img

    def predict(self, image_path):
        if not self.model_loaded:
            return {"error": "Model not loaded"}

        img = self.preprocess(image_path)
        input_img = np.expand_dims(img, axis=0)

        pred = self.model.predict(input_img)[0]

        # For segmentation models
        mask = (pred > 0.5).astype(np.uint8) * 255

        confidence = float(np.mean(pred) * 100)

        has_oil_spill = confidence > OIL_SPILL_DECISION_THRESHOLD_PERCENT

        # Convert images to base64
        def encode_image(image):
            _, buffer = cv2.imencode('.png', image)
            return base64.b64encode(buffer).decode('utf-8')

        original = (img * 255).astype(np.uint8)
        mask_img = mask

        overlay = original.copy()
        overlay[mask_img > 0] = [0, 0, 255]  # red highlight

        return {
            "success": True,
            "confidence": confidence,
            "has_oil_spill": has_oil_spill,
            "original_image": encode_image(original),
            "mask_image": encode_image(mask_img),
            "overlay_image": encode_image(overlay)
        }

detector = Detector()