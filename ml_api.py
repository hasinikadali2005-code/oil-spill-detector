import os

OIL_SPILL_DECISION_THRESHOLD_PERCENT = 50

class Detector:
    def __init__(self):
        # 🔥 Completely disable model loading for deployment
        self.model_loaded = False
        self.model = None
        print("Running in DEMO mode (no ML model)")

    def predict(self, image_path):
        # 🔥 Always return demo result
        return {
            "success": True,
            "confidence": 82.3,
            "has_oil_spill": True,
            "status_text": "Oil Spill Detected",
            "message": "Demo mode (model disabled for deployment)"
        }

detector = Detector()