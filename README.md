# 🌊 Oil Spill Detection System - Complete Solution

A full-stack AI-powered application for detecting oil spills in satellite imagery using deep learning, Spring Boot, and Flask.

## 📦 System Components

### 1. **Flask ML API** (Python Backend)
- **Port:** 5000
- **Language:** Python
- **Purpose:** Model inference and prediction
- **Key Features:**
  - Loads trained Keras model
  - Preprocesses images (256×256 resize, normalization)
  - Runs neural network inference
  - Creates overlay visualization with RED highlights
  - Encodes output as base64 PNG

### 2. **Spring Boot API** (Java Backend)
- **Port:** 8080
- **Language:** Java 17
- **Purpose:** REST API and file handling
- **Key Features:**
  - Receives images from frontend
  - Validates file uploads
  - Forwards to Flask API
  - Exception handling and error responses
  - CORS support for frontend

### 3. **Frontend UI** (HTML/JavaScript)
- **Served by:** Spring Boot
- **URL:** http://localhost:8080
- **Features:**
  - Drag-and-drop file upload
  - Real-time prediction display
  - Confidence visualization with animated bar
  - Overlay image display with RED oil spill highlights
  - Responsive mobile design

### 4. **Trained Model** (Keras)
- **File:** `model/oil_spill_model.keras`
- **Input:** 256×256×3 normalized image
- **Output:** Pixel-wise prediction (0-1 values)
- **Threshold:** 0.3 (configurable)

## 🔄 Complete Data Flow

```
USER ACTION
    ↓
[Frontend: HTML/JS] ← User uploads image
    ↓
HTTP POST /api/predict (multipart/form-data)
    ↓
[Spring Boot] ← Receive & validate file
    ↓
HTTP POST /predict (to Flask API)
    ↓
[Flask ML API] ← Load image, preprocess
    ↓
[Keras Model] ← Run inference on 256×256 normalized image
    ↓
[Flask Processing] ← Apply threshold 0.3, create RED overlay, base64 encode
    ↓
JSON Response with overlay_image (base64 PNG)
    ↓
[Spring Boot] ← Parse response, return to client
    ↓
HTTP 200 OK + JSON Response
    ↓
[Frontend JavaScript] ← Parse JSON, display overlay image & confidence
    ↓
USER SEES RESULT
    - Overlay image with red highlights
    - Confidence percentage
    - Oil spill status (detected/safe)
```

## 📁 Project Structure

```
oil_spill_detection_model/
│
├── model/
│   └── oil_spill_model.keras          ← Trained model (required)
│
├── ml_api.py                           ← Flask ML API main file
├── app.py                              ← Flask UI (optional legacy)
│
├── QUICK_START.md                     ← Quick startup guide ⭐ START HERE
├── INTEGRATION_GUIDE.md               ← Full architecture documentation
├── test_pipeline.py                   ← Automated test suite
├── startup.sh                          ← Bash startup script
│
└── spring-backend/                    ← Spring Boot application
    ├── pom.xml                        ← Maven dependencies
    ├── README.md                      ← Spring Boot documentation
    │
    ├── src/main/
    │   ├── java/com/oilspill/
    │   │   ├── OilSpillApplication.java        ← Main class
    │   │   ├── controller/
    │   │   │   └── OilSpillController.java     ← REST endpoints
    │   │   ├── service/
    │   │   │   └── OilSpillService.java        ← Business logic
    │   │   ├── dto/
    │   │   │   └── PredictionResponse.java     ← Response model
    │   │   ├── exception/
    │   │   │   ├── ApiException.java
    │   │   │   └── FileUploadException.java
    │   │   └── config/
    │   │       ├── RestTemplateConfig.java     ← HTTP client
    │   │       └── GlobalExceptionHandler.java ← Error handling
    │   │
    │   ├── resources/
    │   │   ├── application.properties          ← Configuration
    │   │   └── static/
    │   │       └── index.html                  ← Frontend UI
    │   │
    │   └── test/                               ← Unit tests
    │
    └── target/                                 ← Built JAR file
```

## 🚀 Quick Start (5 minutes)

### Prerequisites
```bash
# Python packages
pip install flask keras tensorflow opencv-python numpy requests

# Java & Maven
# Download Java 17: https://www.oracle.com/java/technologies/
# Download Maven: https://maven.apache.org/
```

### Terminal 1: Start Flask ML API
```bash
cd c:\Users\hasin\OneDrive\Desktop\oil_spill_detection_model
python ml_api.py
```

Wait for output:
```
✓ Model loaded successfully
Running on http://0.0.0.0:5000
```

### Terminal 2: Start Spring Boot
```bash
cd c:\Users\hasin\OneDrive\Desktop\oil_spill_detection_model\spring-backend
mvn clean install
mvn spring-boot:run
```

Wait for output:
```
Tomcat started on port(s): 8080
Oil Spill Detection Backend Started
```

### Browser: Open Frontend
```
http://localhost:8080
```

✅ Done! System ready for predictions.

## 🧪 Testing

### Option 1: Automated Test Suite
```bash
python test_pipeline.py
```

This runs 5 tests:
1. Flask health check
2. Spring Boot health check
3. Frontend access
4. Flask prediction (with generated test image)
5. Spring Boot prediction (complete pipeline)

### Option 2: Manual Testing

**Test Flask API:**
```bash
curl http://127.0.0.1:5000/health
```

**Test Spring Boot:**
```bash
curl http://localhost:8080/api/health
```

**Test Predictions:**
```bash
curl -X POST -F "file=@image.jpg" http://localhost:8080/api/predict
```

## 📊 API Reference

### Flask ML API

**POST /predict**
```
Request:
  Content-Type: multipart/form-data
  Body: file (image in PNG, JPG, BMP, GIF, JPEG)

Response (200 OK):
{
  "success": true,
  "confidence": 85.5,
  "has_oil_spill": true,
  "overlay_image": "data:image/png;base64,iVBORw0KGgo...",
  "prediction_map": "data:image/png;base64,iVBORw0KGgo..."
}

Response (400/500 Error):
{
  "success": false,
  "error": "Invalid file format..."
}
```

**GET /health**
```
Response:
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "model/oil_spill_model.keras"
}
```

### Spring Boot API

**POST /api/predict**
```
Request:
  Content-Type: multipart/form-data
  Body: file (image in PNG, JPG, BMP, GIF, JPEG)

Response: (same as Flask, HTTP 200/400/500)
```

**GET /api/health**
```
Response:
{
  "status": "healthy",
  "service": "Oil Spill Detection API",
  "ml_api_status": "connected"
}
```

## ⚙️ Configuration

### Flask (`ml_api.py`, lines 13-20)
```python
MODEL_PATH = 'model/oil_spill_model.keras'
IMAGE_SIZE = (256, 256)                    # Model input size
PREDICTION_THRESHOLD = 0.3                 # Binary mask threshold
OIL_SPILL_COLOR = [255, 0, 0]             # RED in BGR
MAX_FILE_SIZE = 20 * 1024 * 1024          # 20MB limit
```

### Spring Boot (`application.properties`)
```properties
flask.api.url=http://127.0.0.1:5000/predict
server.port=8080
spring.servlet.multipart.max-file-size=20MB
logging.level.com.oilspill=DEBUG
```

## 📝 Key Features

✅ **Complete Pipeline**
- Frontend UI → Spring Boot → Flask ML API → Keras Model

✅ **Image Processing**
- Resize to 256×256 (model input size)
- Normalize to [0, 1] range
- Threshold 0.3 for binary classification

✅ **Visualization**
- Original image with RED overlay on detected regions
- Alpha blending (60% red, 40% original)
- Base64 PNG encoding for easy transmission

✅ **Error Handling**
- File validation (type, size, extension)
- API communication error handling
- Detailed error messages

✅ **User Experience**
- Modern responsive UI
- Drag-and-drop file upload
- Real-time confidence visualization
- Animated progress bar

✅ **Production Ready**
- CORS support
- Request timeouts
- Comprehensive logging
- Exception handling

## 🔐 Security Features

1. **File Upload Security**
   - Whitelist allowed extensions: PNG, JPG, JPEG, BMP, GIF
   - File size limit: 20MB
   - Secure filename sanitization

2. **API Security**
   - Input validation
   - Error message sanitization
   - No sensitive data exposure

3. **Architecture**
   - Flask API accessible only internally (127.0.0.1)
   - Spring Boot provides public interface
   - Firewall-friendly

## 📈 Performance

- **Model Loading:** ~3-5 seconds (once at startup)
- **Image Preprocessing:** ~100-200ms
- **Inference Time:** ~500ms-2s (depending on model)
- **Overlay Generation:** ~100-300ms
- **Total Latency:** ~1-3 seconds end-to-end

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Flask won't start | Check Python installation: `python --version` |
| Model not found | Verify: `ls model/oil_spill_model.keras` |
| Port 5000 in use | `netstat -ano \| findstr :5000` then kill process |
| Port 8080 in use | `netstat -ano \| findstr :8080` then kill process |
| Spring can't find Flask | Check `application.properties` Flask URL |
| Frontend blank | Check browser console for JavaScript errors |

See [QUICK_START.md](QUICK_START.md) for detailed troubleshooting.

## 📚 Documentation Files

1. **[QUICK_START.md](QUICK_START.md)** ⭐ Start here
   - Step-by-step setup
   - Quick testing guide
   - Troubleshooting

2. **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)**
   - Complete architecture
   - Data flow diagram
   - Detailed pipeline explanation

3. **[spring-backend/README.md](spring-backend/README.md)**
   - Spring Boot setup
   - API endpoints
   - Docker support

4. **Code Comments**
   - `ml_api.py` - Flask ML processing
   - `OilSpillController.java` - REST endpoints
   - `OilSpillService.java` - Flask integration
   - `index.html` - Frontend logic

## 🔄 Typical Workflow

1. **Start Services**
   ```bash
   # Terminal 1
   python ml_api.py
   
   # Terminal 2
   cd spring-backend && mvn spring-boot:run
   ```

2. **Open Browser**
   ```
   http://localhost:8080
   ```

3. **Upload Image**
   - Click upload area or drag image
   - Supported: PNG, JPG, JPEG, BMP, GIF

4. **Get Prediction**
   - Click "Predict" button
   - Wait 1-3 seconds for analysis
   - View results:
     - Overlay image with red highlights
     - Confidence percentage
     - Oil spill status

5. **Analyze Results**
   - Higher confidence = more certain
   - Red regions = detected oil spill
   - Green badge = no spill detected

## 🎓 Understanding the Model

**Input:** 256×256 pixel image (normalized to [0,1])

**Processing:**
- Convolutional layers extract features
- Pooling reduces dimensions
- Dense/output layers predict oil spill

**Output:** Probability map (0-1 values per pixel)

**Threshold:** 0.3
- Pixel > 0.3 → Oil spill
- Pixel ≤ 0.3 → No oil spill

**Confidence:** Percentage of detected pixels

## 📞 Support

For issues or questions:
1. Check [QUICK_START.md](QUICK_START.md) troubleshooting
2. Review code comments in relevant file
3. Check application logs (terminal output)
4. Verify health endpoints:
   - Flask: `curl http://127.0.0.1:5000/health`
   - Spring: `curl http://localhost:8080/api/health`

## 📄 License

Oil Spill Detection System v1.0.0  
Status: Production Ready ✅

---

**Last Updated:** March 19, 2026

**Quick Links:**
- [Quick Start Guide](QUICK_START.md)
- [Integration Architecture](INTEGRATION_GUIDE.md)
- [Test Pipeline](test_pipeline.py)
