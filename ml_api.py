import os
import cv2
import numpy as np
import base64

OIL_SPILL_DECISION_THRESHOLD_PERCENT = 35

class Detector:
    def __init__(self):
        self.model_loaded = False
        self.model = None

        try:
            from tensorflow.keras.models import load_model

            model_path = "model/oil_spill_model.keras"

            if os.path.exists(model_path):
                self.model = load_model(model_path)
                self.model_loaded = True
                print("Model loaded successfully")
            else:
                print("Model file not found")

        except Exception as e:
            print("TensorFlow not available, running in DEMO mode:", e)

    def preprocess(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.resize(img, (256, 256))
        img = img / 255.0
        return img

    def encode_image(self, image):
        _, buffer = cv2.imencode('.png', image)
        return base64.b64encode(buffer).decode('utf-8')

    def _build_overlay(self, base_image_bgr, mask_u8):
        overlay = base_image_bgr.copy()
        red_layer = np.zeros_like(base_image_bgr)
        red_layer[:, :, 2] = 255
        # Blend only masked regions so underlying texture remains visible.
        overlay[mask_u8 > 0] = cv2.addWeighted(
            overlay[mask_u8 > 0],
            0.45,
            red_layer[mask_u8 > 0],
            0.55,
            0,
        )
        return overlay

    def _predict_demo(self, original_resized):
        gray = cv2.cvtColor(original_resized, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Heuristic demo mask: dark/low-reflectance regions are treated as potential spill.
        _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        dark_ratio = float(np.mean(gray < 85))
        mask_ratio = float(np.mean(mask > 0))

        # Favor large contiguous slick-like regions over scattered noise pixels.
        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        largest_region_ratio = 0.0
        if num_labels > 1:
            largest_area = int(np.max(stats[1:, cv2.CC_STAT_AREA]))
            total_pixels = int(mask.shape[0] * mask.shape[1])
            largest_region_ratio = largest_area / max(total_pixels, 1)

        score = (
            0.35 * dark_ratio
            + 0.35 * mask_ratio
            + 0.30 * largest_region_ratio
        )
        confidence = float(np.clip(score * 100.0, 1.0, 99.0))
        has_oil_spill = confidence >= OIL_SPILL_DECISION_THRESHOLD_PERCENT

        overlay = self._build_overlay(original_resized, mask)

        return {
            "success": True,
            "confidence": round(confidence, 2),
            "has_oil_spill": bool(has_oil_spill),
            "status_text": "Oil Spill Detected" if has_oil_spill else "No Spill",
            "original_image": self.encode_image(original_resized),
            "mask_image": self.encode_image(mask),
            "overlay_image": self.encode_image(overlay),
        }

    def predict(self, image_path):
        try:
            # Load original image
            original = cv2.imread(image_path)
            if original is None:
                return {
                    "success": False,
                    "error": "Unable to read input image"
                }
            original_resized = cv2.resize(original, (256, 256))

            # =========================
            # 🔥 DEMO MODE (NO MODEL)
            # =========================
            if not self.model_loaded:
                return self._predict_demo(original_resized)

            # =========================
            # 🔥 REAL MODEL PREDICTION
            # =========================
            img = self.preprocess(image_path)
            input_img = np.expand_dims(img, axis=0)

            pred = self.model.predict(input_img, verbose=0)[0]

            if np.ndim(pred) >= 2:
                pred_map = pred[:, :, 0] if np.ndim(pred) == 3 else pred
                mask = (pred_map > 0.5).astype(np.uint8) * 255
                mask = cv2.resize(mask, (256, 256), interpolation=cv2.INTER_NEAREST)
                confidence = float(np.mean(pred_map) * 100)
            else:
                score = float(np.squeeze(pred))
                confidence = float(np.clip(score * 100, 0.0, 100.0))
                mask = np.zeros((256, 256), dtype=np.uint8)

            has_oil_spill = confidence > OIL_SPILL_DECISION_THRESHOLD_PERCENT

            overlay = self._build_overlay(original_resized, mask)

            return {
                "success": True,
                "confidence": round(confidence, 2),
                "has_oil_spill": has_oil_spill,
                "status_text": "Oil Spill Detected" if has_oil_spill else "No Spill",
                "original_image": self.encode_image(original_resized),
                "mask_image": self.encode_image(mask),
                "overlay_image": self.encode_image(overlay)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


detector = Detector()