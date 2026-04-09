# 🚀 Oil Spill Detection - Quick Start Guide

## Complete System Overview

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND (Browser)                                      │
│  http://localhost:8080                                   │
│  - Upload satellite image                                │
│  - Click "Predict" button                                │
│  - View results with overlay                             │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP POST /api/predict
                 ▼
┌─────────────────────────────────────────────────────────┐
│  SPRING BOOT BACKEND (Java)                              │
│  http://localhost:8080                                   │
│  - Receives image from frontend                          │
│  - Validates file                                        │
│  - Forwards to Flask API                                 │
│  - Returns prediction to frontend                        │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP POST /predict
                 │ (multipart/form-data)
                 ▼
┌─────────────────────────────────────────────────────────┐
│  FLASK ML API (Python)                                   │
│  http://127.0.0.1:5000                                   │
│  - Receives image from Spring Boot                       │
│  - Preprocesses: 256x256, normalize                      │
│  - Runs model inference                                  │
│  - Threshold 0.3 for binary mask                         │
│  - Creates RED overlay on oil spill regions              │
│  - Encodes as base64 PNG                                 │
│  - Returns JSON response                                 │
└────────────────┬────────────────────────────────────────┘
                 │ JSON Response
                 │ (overlay_image, prediction_map)
                 ▼
┌─────────────────────────────────────────────────────────┐
│  KERAS/TENSORFLOW MODEL                                  │
│  model/oil_spill_model.keras                             │
│  - Trained neural network                                │
│  - Detects oil spills in satellite imagery               │
└─────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### Python (for Flask ML API)
- Python 3.8 or higher
- Flask
- Keras
- TensorFlow
- OpenCV (cv2)
- NumPy

Install Python packages:
```bash
pip install flask keras opencv-python numpy tensorflow
```

### Java (for Spring Boot)
- Java 17 or higher
- Maven 3.6 or higher

## 🎯 Step-by-Step Startup (Windows)

### Step 1: Start Flask ML API
```bash
# Navigate to project root
cd c:\Users\hasin\OneDrive\Desktop\oil_spill_detection_model

# Run Flask API (will start on port 5000)
python ml_api.py
```

**Expected Output:**
```
============================================================
Oil Spill Detection ML API Server
============================================================
Model Status: ✓ Loaded
API Endpoint: http://0.0.0.0:5000/predict
Health Check: http://0.0.0.0:5000/health
============================================================
```

✅ **Flask is ready when you see:**
- "Model Status: ✓ Loaded"
- "WARNING: This is a development server..."
- Running on http://0.0.0.0:5000

⏱️ **Leave this terminal open!**

---

### Step 2: Start Spring Boot Backend (New Terminal)
```bash
# Navigate to Spring Backend
cd c:\Users\hasin\OneDrive\Desktop\oil_spill_detection_model\spring-backend

# Build the project (first time only)
mvn clean install

# Run Spring Boot (will start on port 8080)
mvn spring-boot:run
```

**Expected Output:**
```
[INFO] Building Oil Spill Detection Backend
[INFO] ======================== BUILD SUCCESS ========================
============================================================
Oil Spill Detection Backend Started
============================================================
API Endpoint: http://localhost:8080/api/predict
Flask ML API: http://127.0.0.1:5000/predict
============================================================
```

✅ **Spring Boot is ready when you see:**
- "Tomcat started on port(s): 8080"
- Application startup/banner message
- No red ERROR lines

⏱️ **Leave this terminal open!**

---

### Step 3: Access Frontend (Browser)
```
Open: http://localhost:8080
```

**You should see:**
- Modern UI with upload area
- "Click to upload" section with drag & drop support
- "Predict" and "Clear" buttons

---

## 🧪 Testing the Pipeline

### Test 1: Flask API Health
```bash
# In a new terminal or PowerShell
curl http://127.0.0.1:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "model/oil_spill_model.keras"
}
```

### Test 2: Spring Boot Health
```bash
curl http://localhost:8080/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Oil Spill Detection API",
  "ml_api_status": "connected"
}
```

### Test 3: Full Pipeline (Image Upload)
```bash
# Using PowerShell on Windows
$FilePath = "C:\path\to\test_image.jpg"
$Uri = "http://localhost:8080/api/predict"
$Form = @{
    file = Get-Item -Path $FilePath
}
Invoke-WebRequest -Uri $Uri -Method Post -Form $Form | ConvertTo-Json
```

Or using curl on Windows:
```bash
curl -X POST -F "file=@C:\path\to\test_image.jpg" http://localhost:8080/api/predict
```

## 📊 Data Flow Example

### User Action
1. Opens browser to http://localhost:8080
2. Uploads satellite image (test.jpg)
3. Clicks "Predict" button

### Pipeline Execution

**Frontend (Browser):**
```javascript
// test.jpg (500KB)
fetch('http://localhost:8080/api/predict', {
  method: 'POST',
  body: formData  // Contains test.jpg
})
```

**Spring Boot (Log Output):**
```
📥 Received image upload request: test.jpg
📤 Forwarding to OilSpillService for processing...
📤 Sending request to Flask API: http://127.0.0.1:5000/predict
✓ Response received from Flask API
📤 Returning prediction response to frontend
```

**Flask API (Log Output):**
```
✓ File received: test.jpg
✓ Image preprocessing complete
  - Original size: (512, 512, 3)
  - Batch size: (1, 256, 256, 3)
🧠 Running model inference...
  - Model: model/oil_spill_model.keras
✓ Model inference complete
  - Output shape: (1, 256, 256, 1)
🎯 Creating binary mask with threshold 0.3
  - Detected pixels: 12540 / 65536
  - Confidence: 19.13%
🎨 Creating overlay image with RED highlights
```

**Frontend (Display):**
```
✓ Analysis completed successfully!

Results shown:
- Overlay image with RED highlights
- Confidence: 19.13%
- Status: ✅ No Oil Spill (< 50% threshold)
```

## ⚙️ Configuration Files

### Flask Configuration
File: `ml_api.py` (lines 13-20)
```python
MODEL_PATH = 'model/oil_spill_model.keras'
IMAGE_SIZE = (256, 256)
PREDICTION_THRESHOLD = 0.3
OIL_SPILL_COLOR = [255, 0, 0]  # RED
```

### Spring Boot Configuration
File: `spring-backend/src/main/resources/application.properties`
```properties
flask.api.url=http://127.0.0.1:5000/predict
server.port=8080
spring.servlet.multipart.max-file-size=20MB
```

## 🔧 Troubleshooting

### Issue: Flask API won't start
**Error:** "No module named 'keras'"

**Solution:**
```bash
pip install keras tensorflow opencv-python numpy flask
```

### Issue: Spring Boot can't connect to Flask
**Error:** "Failed to communicate with Flask API"

**Solution:**
1. Verify Flask is running: `curl http://127.0.0.1:5000/health`
2. Check `application.properties` has correct Flask URL
3. Restart Spring Boot

### Issue: Model file not found
**Error:** "Model file not found: model/oil_spill_model.keras"

**Solution:**
```bash
# Verify file exists
ls -la c:\Users\hasin\OneDrive\Desktop\oil_spill_detection_model\model\

# Should show:
# oil_spill_model.keras
```

### Issue: Port 8080 already in use
**Error:** "Address already in use"

**Solution:**
```bash
# Find and kill process on port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Or change port in application.properties:
# server.port=8081
```

### Issue: Port 5000 already in use
**Error:** "Address already in use"

**Solution:**
```bash
# Kill Python process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 📁 Project Structure

```
oil_spill_detection_model/
├── model/
│   └── oil_spill_model.keras          ← Trained model
├── ml_api.py                           ← Flask ML API
├── app.py                              ← Flask UI (optional)
├── INTEGRATION_GUIDE.md               ← Full architecture docs
├── QUICK_START.md                     ← This file
│
└── spring-backend/                    ← Spring Boot backend
    ├── pom.xml                        ← Maven config
    ├── src/main/java/com/oilspill/
    │   ├── OilSpillApplication.java   ← Main class
    │   ├── controller/
    │   │   └── OilSpillController.java ← REST endpoints
    │   ├── service/
    │   │   └── OilSpillService.java    ← Business logic
    │   ├── exception/                  ← Error handling
    │   ├── dto/                        ← Data models
    │   └── config/                     ← Configuration
    │
    └── src/main/resources/
        ├── application.properties       ← Config file
        └── static/
            └── index.html              ← Frontend UI
```

## 📞 API Reference

### Flask Endpoints

**POST /predict**
```
URL: http://127.0.0.1:5000/predict
Content-Type: multipart/form-data
Parameter: file (image)

Response:
{
  "success": true,
  "confidence": 85.5,
  "has_oil_spill": true,
  "overlay_image": "data:image/png;base64,...",
  "prediction_map": "data:image/png;base64,..."
}
```

**GET /health**
```
URL: http://127.0.0.1:5000/health
Response:
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "model/oil_spill_model.keras"
}
```

### Spring Boot Endpoints

**POST /api/predict**
```
URL: http://localhost:8080/api/predict
Content-Type: multipart/form-data
Parameter: file (image)

Response: (same as Flask)
{
  "success": true,
  "confidence": 85.5,
  "has_oil_spill": true,
  "overlay_image": "data:image/png;base64,...",
  "prediction_map": "data:image/png;base64,..."
}
```

**GET /api/health**
```
URL: http://localhost:8080/api/health
Response:
{
  "status": "healthy",
  "service": "Oil Spill Detection API",
  "ml_api_status": "connected"
}
```

## 🎓 Understanding the ML Pipeline

1. **Image Preprocessing**
   - Resize: Any size → 256×256 pixels
   - Normalize: [0-255] → [0-1] (divide by 255)
   - Batch: Single image → batch of 1

2. **Model Inference**
   - Input: 256×256×3 normalized image
   - Model: Trained Keras neural network
   - Output: Prediction map (0-1 values)

3. **Binary Mask Creation**
   - Threshold: 0.3 (tunable)
   - Result: 1 where prediction > 0.3, else 0
   - Interpretation: 1 = oil spill, 0 = no spill

4. **Overlay Generation**
   - Load original image
   - Color detected regions: RED ([255, 0, 0])
   - Blend: 60% red, 40% original (alpha blending)
   - Output: PNG image

5. **Confidence Calculation**
   - Count detected pixels (1s in mask)
   - Percentage: (detected / total) × 100
   - Display: Confidence bar in UI

## 🔐 Security Notes

1. File Upload Validation
   - Extensions: PNG, JPG, JPEG, BMP, GIF only
   - Size limit: 20MB
   - MIME type checked in both frontend and backend

2. Input Sanitization
   - Filenames sanitized with `secure_filename`
   - No arbitrary file paths allowed

3. Error Handling
   - No sensitive information in error messages
   - Stack traces only in development logs

## 🎯 Next Steps

1. ✅ Start Flask ML API (port 5000)
2. ✅ Start Spring Boot Backend (port 8080)
3. ✅ Open http://localhost:8080 in browser
4. ✅ Test with sample satellite images
5. 📊 Monitor logs in terminal windows
6. 🔧 Adjust threshold/parameters as needed

## 📚 Documentation Links

- [Full Integration Guide](INTEGRATION_GUIDE.md)
- [Flask ML API Code](ml_api.py)
- [Spring Boot README](spring-backend/README.md)
- [Frontend Code](spring-backend/src/main/resources/static/index.html)

---

**Status:** ✅ Ready for Production  
**Last Updated:** March 19, 2026  
**Questions?** Check the integration guide or code comments
