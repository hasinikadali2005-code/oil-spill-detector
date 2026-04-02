import os
import base64

OIL_SPILL_DECISION_THRESHOLD_PERCENT = 50


def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class Detector:
    def __init__(self):
        self.model_loaded = False
        self.model = None
        print("Running in DEMO mode (no ML model)")

    def predict(self, image_path):
        try:
            # 🔥 Convert uploaded image to base64
            img_base64 = image_to_base64(image_path)

            return {
                "success": True,
                "confidence": 82.3,
                "has_oil_spill": True,
                "status_text": "Oil Spill Detected",
                "message": "Demo mode (model disabled for deployment)",

                # 🔥 IMPORTANT (for UI)
                "original_image": f"data:image/png;base64,{img_base64}",
                "mask_image": f"data:image/png;base64,{img_base64}",
                "overlay_image": f"data:image/png;base64,{img_base64}"  # dummy
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


detector = Detector()