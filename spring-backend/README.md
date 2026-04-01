# Oil Spill Detection Spring Boot Backend

Spring Boot REST API backend for oil spill detection using Flask ML API integration.

## Project Structure

```
spring-backend/
├── pom.xml                          # Maven configuration
├── src/main/
│   ├── java/com/oilspill/
│   │   ├── OilSpillApplication.java # Main application class
│   │   ├── controller/
│   │   │   └── OilSpillController.java      # REST endpoints
│   │   ├── service/
│   │   │   └── OilSpillService.java         # Business logic & Flask API calls
│   │   ├── dto/
│   │   │   └── PredictionResponse.java      # Response DTO
│   │   ├── exception/
│   │   │   ├── ApiException.java            # Custom API exception
│   │   │   └── FileUploadException.java     # File upload exception
│   │   └── config/
│   │       ├── RestTemplateConfig.java      # HTTP client configuration
│   │       └── GlobalExceptionHandler.java  # Centralized exception handling
│   └── resources/
│       └── application.properties            # Application configuration
└── README.md                        # This file
```

## Prerequisites

- Java 17 or higher
- Maven 3.6+
- Flask ML API running on `http://127.0.0.1:5000`

## Setup & Installation

1. **Navigate to spring-backend directory:**
   ```bash
   cd spring-backend
   ```

2. **Build the project:**
   ```bash
   mvn clean install
   ```

3. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

   Or directly:
   ```bash
   java -jar target/oil-spill-detection-1.0.0.jar
   ```

The application will start on `http://localhost:8080`

## API Endpoints

### 1. Upload Image for Prediction
**Endpoint:** `POST /api/predict`

**Request:**
```bash
curl -X POST -F "file=@image.jpg" http://localhost:8080/api/predict
```

**Response (Success - 200 OK):**
```json
{
  "success": true,
  "confidence": 85.5,
  "has_oil_spill": true,
  "overlay_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAFBQIAX8jx0gAAAABJRU5ErkJggg==",
  "prediction_map": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "success": false,
  "error_code": "FILE_ERROR",
  "error": "Invalid file format. Allowed formats: [png, jpg, jpeg, bmp, gif]"
}
```

### 2. Health Check
**Endpoint:** `GET /api/health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Oil Spill Detection API",
  "ml_api_status": "connected"
}
```

## Configuration

Edit `src/main/resources/application.properties` to customize:

```properties
# Server port
server.port=8080

# Flask ML API URL
flask.api.url=http://127.0.0.1:5000/predict

# File upload limits
spring.servlet.multipart.max-file-size=20MB
spring.servlet.multipart.max-request-size=20MB

# Logging level
logging.level.com.oilspill=DEBUG
```

## Features

✅ **REST API for image upload and prediction**
- POST /api/predict - Analyze image for oil spills
- GET /api/health - Check service health

✅ **File validation**
- File type validation (PNG, JPG, JPEG, BMP, GIF)
- File size validation (max 20MB)
- Empty file detection

✅ **Exception handling**
- Custom exceptions for different error scenarios
- Global exception handler
- Detailed error messages

✅ **Flask ML API integration**
- RestTemplate for HTTP communication
- Configurable API endpoint
- Timeout management

✅ **CORS support**
- Cross-Origin enabled for frontend integration

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| FILE_ERROR | 400 | File validation failed |
| API_ERROR | 500 | Flask API communication error |
| INTERNAL_ERROR | 500 | Unexpected server error |
| HEALTH_CHECK_ERROR | 503 | Service unavailable |

## Integration with Frontend

```javascript
// JavaScript example
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8080/api/predict', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => {
  console.log('Prediction:', data);
  // Display overlay_image in your UI
});
```

## Docker Support (Optional)

To containerize the application, create a `Dockerfile`:

```dockerfile
FROM openjdk:17-jdk-slim
COPY target/oil-spill-detection-1.0.0.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

Build and run:
```bash
docker build -t oil-spill-api .
docker run -p 8080:8080 oil-spill-api
```

## Dependencies

- **Spring Boot 3.1.5** - Web framework
- **RestTemplate** - HTTP client
- **Lombok** - Reduce boilerplate
- **JUnit 5** - Testing

## License

By: Oil Spill Detection Team
