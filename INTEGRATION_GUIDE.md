# Oil Spill Detection - Full Integration Pipeline

## 🔄 System Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Browser)                        │
│              spring-backend/src/main/resources/static/            │
│                        index.html                                 │
│  ✓ File upload (drag & drop)                                     │
│  ✓ Displays prediction results                                   │
│  ✓ Shows overlay image with confidence                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                  HTTP POST /api/predict
                    (MultipartFile: image)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            SPRING BOOT BACKEND (Java REST API)                   │
│                  Port: 8080                                       │
│                                                                   │
│  OilSpillController                                              │
│  ├─ POST /api/predict - Receives image from frontend             │
│  └─ GET /api/health - Service status check                       │
│                                                                   │
│  OilSpillService                                                 │
│  ├─ validateFile() - Checks file type, size, extension          │
│  ├─ callFlaskAPI() - Forwards to Flask ML API                   │
│  └─ predictOilSpill() - Orchestrates the flow                   │
│                                                                   │
│  GlobalExceptionHandler                                          │
│  ├─ Catches FileUploadException                                  │
│  ├─ Catches ApiException                                         │
│  └─ Returns proper HTTP status & error messages                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                  HTTP POST http://127.0.0.1:5000/predict
                   (MultipartFile: image)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              FLASK ML API (Python REST API)                       │
│                  Port: 5000                                       │
│         ml_api.py & app.py                                       │
│                                                                   │
│  OilSpillDetector                                                │
│  ├─ __init__() - Loads model from model/oil_spill_model.keras  │
│  ├─ preprocess_image() - Resizes to 256x256, normalizes         │
│  ├─ predict_with_overlay() - Runs inference                     │
│  │   ├─ Applies threshold 0.3 to create binary mask             │
│  │   └─ Creates RED overlay on oil spill regions                │
│  └─ _create_overlay() - Encodes result as base64 PNG            │
│                                                                   │
│  POST /predict - ML inference endpoint                           │
│  GET /health - ML API status check                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                  Returns JSON Response:
                  {
                    "success": true,
                    "confidence": 85.5,
                    "has_oil_spill": true,
                    "overlay_image": "data:image/png;base64,...",
                    "prediction_map": "data:image/png;base64,..."
                  }
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            SPRING BOOT BACKEND (Response Processing)            │
│                                                                   │
│  OilSpillService.callFlaskAPI()                                  │
│  ├─ Receives base64 images from Flask                           │
│  ├─ Wraps in PredictionResponse DTO                             │
│  └─ Returns to controller                                        │
│                                                                   │
│  OilSpillController.predictOilSpill()                            │
│  ├─ Receives PredictionResponse                                 │
│  └─ Returns JSON to frontend                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                  HTTP 200 OK Response (JSON)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Browser)                        │
│                                                                   │
│  JavaScript Fetch Handler                                        │
│  ├─ Receives JSON response                                       │
│  ├─ Displays overlay_image as <img src="data:...">             │
│  ├─ Shows confidence percentage & status                         │
│  └─ Updates confidence bar animation                             │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ (for Flask)
- Java 17+ (for Spring Boot)
- Maven 3.6+ (for building)
- Keras model file: `model/oil_spill_model.keras`

### Step 1: Start Flask ML API
```bash
cd c:\Users\hasin\OneDrive\Desktop\oil_spill_detection_model

# Install Python dependencies
pip install flask keras opencv-python numpy tensorflow

# Run Flask API (will start on port 5000)
python ml_api.py
```

Expected output:
```
============================================================
Oil Spill Detection ML API Server
============================================================
Model Status: ✓ Loaded
API Endpoint: http://0.0.0.0:5000/predict
Health Check: http://0.0.0.0:5000/health
============================================================
```

### Step 2: Start Spring Boot Backend
```bash
cd c:\Users\hasin\OneDrive\Desktop\oil_spill_detection_model\spring-backend

# Build the project
mvn clean install

# Run the application (will start on port 8080)
mvn spring-boot:run
```

Expected output:
```
============================================================
Oil Spill Detection Backend Started
============================================================
API Endpoint: http://localhost:8080/api/predict
Flask ML API: http://127.0.0.1:5000/predict
============================================================
```

### Step 3: Access Frontend
1. Open browser to: **http://localhost:8080/**
2. Upload an image
3. Click "Predict" button
4. View results with overlay image

## 📋 Configuration

### Flask API Configuration
File: `ml_api.py`
```python
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'oil_spill_model.keras')
IMAGE_SIZE = (256, 256)
PREDICTION_THRESHOLD = 0.3  # Threshold for binary mask
OIL_SPILL_COLOR = [255, 0, 0]  # RED in BGR format
```

### Spring Boot Configuration
File: `spring-backend/src/main/resources/application.properties`
```properties
# Flask ML API endpoint
flask.api.url=http://127.0.0.1:5000/predict

# File upload limits
spring.servlet.multipart.max-file-size=20MB

# Server port
server.port=8080
```

### Frontend Configuration
File: `spring-backend/src/main/resources/static/index.html`
```javascript
const API_ENDPOINT = 'http://localhost:8080/api/predict';
```

## 🔌 API Endpoints

### Flask ML API

**POST /predict**
- Accepts: `multipart/form-data` with image file
- Returns: JSON with base64 encoded overlay and prediction map
- Status: 200 OK or 400/500 on error

**GET /health**
- Returns: Model and API status
- Status: 200 OK

### Spring Boot API

**POST /api/predict**
- Accepts: `multipart/form-data` with image file
- Forwards to Flask API
- Returns: PredictionResponse JSON
- Status: 200 OK or 400/500 on error

**GET /api/health**
- Returns: Service and ML API status
- Status: 200 OK

### Request Example (Spring Boot)
```bash
curl -X POST -F "file=@satellite_image.jpg" http://localhost:8080/api/predict
```

### Response Example
```json
{
  "success": true,
  "confidence": 85.5,
  "has_oil_spill": true,
  "overlay_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAFBQIAX8jx0gAAAABJRU5ErkJggg==",
  "prediction_map": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
}
```

## 🧪 Testing the Pipeline

### Test 1: Flask API Health
```bash
curl http://127.0.0.1:5000/health
```

### Test 2: Spring Boot Health
```bash
curl http://localhost:8080/api/health
```

### Test 3: Full Prediction Pipeline
```bash
# Upload a test image
curl -X POST -F "file=@test_image.jpg" http://localhost:8080/api/predict
```

## 📊 Data Flow Details

### 1. Frontend → Spring Boot
- User selects image file via HTML input
- Frontend validates file (type, size)
- JavaScript Fetch API sends POST request with `FormData`
- Content-Type: `multipart/form-data`

**Frontend Code Location:**
[spring-backend/src/main/resources/static/index.html](spring-backend/src/main/resources/static/index.html) - Lines 400-430

### 2. Spring Boot → Flask
- `OilSpillController` receives image
- `OilSpillService.validateFile()` checks file properties
- `OilSpillService.callFlaskAPI()` forwards to Flask using RestTemplate
- HTTP POST with MultipartFile wrapped in MultiValueMap

**Backend Code Locations:**
- [spring-backend/src/main/java/com/oilspill/controller/OilSpillController.java](spring-backend/src/main/java/com/oilspill/controller/OilSpillController.java#L51)
- [spring-backend/src/main/java/com/oilspill/service/OilSpillService.java](spring-backend/src/main/java/com/oilspill/service/OilSpillService.java#L131)

### 3. Flask ML API Processing
- Receives image from Spring Boot
- `OilSpillDetector.preprocess_image()` resizes to 256×256 and normalizes
- `OilSpillDetector.predict_with_overlay()` runs model prediction
- Applies threshold 0.3 to create binary mask
- `_create_overlay()` creates RED overlay on detected regions
- Encodes result as base64 PNG
- Returns JSON with overlay_image and prediction_map

**ML Code Location:**
[ml_api.py](ml_api.py) - OilSpillDetector class

### 4. Spring Boot → Frontend
- Response from Flask parsed into PredictionResponse DTO
- Returned as JSON to frontend
- HTTP 200 OK with response body

### 5. Frontend Display
- JavaScript receives JSON response
- Sets `<img src="data:image/png;base64,...">` for overlay
- Updates confidence bar and status
- Shows animation and success message

**Frontend Display Code:**
[spring-backend/src/main/resources/static/index.html](spring-backend/src/main/resources/static/index.html#L435-L460)

## ⚠️ Error Handling

### File Validation Errors
- Empty file → 400 Bad Request
- Invalid extension → 400 Bad Request
- File too large → 413 Payload Too Large
- Invalid MIME type → 400 Bad Request

### API Communication Errors
- Flask API timeout → 500 Internal Server Error
- Connection refused → 500 Internal Server Error
- Invalid response → 500 Internal Server Error

### ML Processing Errors
- Model load failure → Service doesn't start
- Image preprocessing failure → 500 Error
- Model inference failure → 500 Error

All errors return structured JSON:
```json
{
  "success": false,
  "error_code": "FILE_ERROR",
  "error": "Invalid file format..."
}
```

## 📁 Complete Project Structure

```
oil_spill_detection_model/
├── model/
│   └── oil_spill_model.keras           # Trained Keras model
│
├── ml_api.py                           # Flask ML API
├── app.py                              # (legacy Flask UI - optional)
│
├── static/
│   ├── uploads/                        # Uploaded images storage
│   └── outputs/                        # Prediction results storage
│
├── templates/
│   └── index.html                      # (legacy Flask UI template - optional)
│
└── spring-backend/                     # Spring Boot application
    ├── pom.xml                         # Maven configuration
    ├── README.md                       # Spring Boot documentation
    │
    ├── src/main/
    │   ├── java/com/oilspill/
    │   │   ├── OilSpillApplication.java          # Main app class
    │   │   ├── controller/
    │   │   │   └── OilSpillController.java       # REST endpoints
    │   │   ├── service/
    │   │   │   └── OilSpillService.java          # Business logic
    │   │   ├── dto/
    │   │   │   └── PredictionResponse.java       # Response model
    │   │   ├── exception/
    │   │   │   ├── ApiException.java
    │   │   │   └── FileUploadException.java
    │   │   └── config/
    │   │       ├── RestTemplateConfig.java       # HTTP client config
    │   │       └── GlobalExceptionHandler.java   # Error handling
    │   │
    │   └── resources/
    │       ├── application.properties            # Configuration
    │       └── static/
    │           └── index.html                    # Frontend UI
```

## 🔐 Security Considerations

1. **File Upload Validation**
   - File extension whitelist: PNG, JPG, JPEG, BMP, GIF
   - File size limit: 20MB
   - MIME type validation in both frontend and backend

2. **API Communication**
   - Flask API accessible only internally (127.0.0.1)
   - Spring Boot exposes public API on localhost:8080
   - Consider adding authentication for production

3. **CORS Configuration**
   - Frontend enabled with `@CrossOrigin(origins = "*")`
   - Configure restrictively in production

## 📈 Performance Optimization

1. **Model Loading**
   - Model loaded once at application startup
   - Singleton pattern ensures no redundant loading

2. **Image Processing**
   - Efficient OpenCV operations
   - Base64 encoding for transfer

3. **Timeout Configuration**
   - RestTemplate connection timeout: 10 seconds
   - RestTemplate read timeout: 30 seconds

## 🛠️ Troubleshooting

### Issue: Frontend can't connect to Spring Boot
- Check if Spring Boot is running on port 8080
- Verify firewall settings
- Check CORS configuration

### Issue: Spring Boot can't connect to Flask API
- Check if Flask is running on port 5000
- Verify `flask.api.url` in application.properties
- Check network connectivity: `ping 127.0.0.1`

### Issue: Model not loaded
- Verify model file exists: `model/oil_spill_model.keras`
- Check file path in `ml_api.py`
- Check model file is not corrupted

### Issue: Prediction takes too long
- Check model size and complexity
- Monitor CPU/Memory usage
- Consider GPU acceleration for Flask API

## 📞 Support & Documentation

For detailed documentation, see:
- [Flask ML API Documentation](ml_api.py) - Inline comments
- [Spring Boot Backend Documentation](spring-backend/README.md)
- Architecture diagram in this file

---

**Version:** 1.0.0  
**Last Updated:** March 19, 2026  
**Status:** Production Ready ✓
