package com.oilspill.service;

import com.oilspill.dto.PredictionResponse;
import com.oilspill.exception.ApiException;
import com.oilspill.exception.FileUploadException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/**
 * Service for Oil Spill Detection
 * Handles file validation and communication with Flask ML API
 */
@Service
public class OilSpillService {
    private static final Logger log = LoggerFactory.getLogger(OilSpillService.class);
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Value("${flask.api.url}")
    private String flaskApiUrl;
    
    // Allowed file extensions
    private static final Set<String> ALLOWED_EXTENSIONS = new HashSet<>(
            Arrays.asList("png", "jpg", "jpeg", "bmp", "gif")
    );
    
    // Maximum file size: 20MB
    private static final long MAX_FILE_SIZE = 20 * 1024 * 1024;
    
    /**
     * PIPELINE STEP 2: Process image file and send to Flask ML API for prediction
     * 
     * This is the main orchestration method that coordinates the entire prediction pipeline:
     * Frontend → Spring Boot → Flask API → Spring Boot → Frontend
     *
     * Flow:
     * 1. Validate uploaded file (type, size, extension)
     * 2. Forward file to Flask ML API at http://127.0.0.1:5000/predict
     * 3. Flask runs model inference and returns base64 encoded overlay image
     * 4. Return PredictionResponse to controller, which sends to frontend
     *
     * @param file MultipartFile containing the image from frontend
     * @return PredictionResponse with detection results (confidence, overlay image, etc.)
     * @throws FileUploadException if file validation fails
     * @throws ApiException if API communication fails
     */
    public PredictionResponse predictOilSpill(MultipartFile file) {
        try {
            // ========== STEP 1: Validate Input File ==========
            // Ensures file is not empty, correct type, correct size, and correct extension
            // Prevents sending invalid files to Flask API
            validateFile(file);
            
            log.info("✓ File validation passed: {}", file.getOriginalFilename());
            log.info("Starting prediction pipeline...");
            
            // ========== STEP 2: Call Flask ML API ==========
            // Sends file to Flask API endpoint: http://127.0.0.1:5000/predict
            // Flask will:
            //   - Resize image to 256x256
            //   - Normalize pixels (divide by 255)
            //   - Run model inference
            //   - Apply threshold 0.3 for binary mask
            //   - Create RED overlay on oil spill regions
            //   - Encode result as base64 PNG
            // Returns: PredictionResponse with overlay_image and prediction_map
            PredictionResponse response = callFlaskAPI(file);
            
            // Check if response is valid
            if (response == null) {
                throw new ApiException("RESPONSE_NULL", "No response from Flask API");
            }
            
            log.info("✓ Prediction completed successfully!");
            log.info("  - Confidence: {}%", response.getConfidence());
            log.info("  - Oil Spill Detected: {}", response.getHasOilSpill());
            
            // ========== STEP 3: Return Response to Controller ==========
            // PredictionResponse will be converted to JSON and sent to frontend
            return response;
            
        } catch (FileUploadException e) {
            // File validation failed - return 400 Bad Request
            log.error("✗ File validation error: {}", e.getMessage());
            throw e;
        } catch (ApiException e) {
            // Flask API communication failed - return 500 Internal Server Error
            log.error("✗ API error: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            // Unexpected error - return 500 Internal Server Error
            log.error("✗ Unexpected error during prediction: {}", e.getMessage(), e);
            throw new ApiException("INTERNAL_ERROR", "Unexpected error: " + e.getMessage(), e);
        }
    }
    
    /**
     * Validate uploaded file
     *
     * @param file MultipartFile to validate
     * @throws FileUploadException if validation fails
     */
    private void validateFile(MultipartFile file) {
        // Check if file is empty
        if (file == null || file.isEmpty()) {
            throw new FileUploadException("File is empty or not selected");
        }
        
        // Check file size
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new FileUploadException(
                    String.format("File size exceeds maximum limit of 20MB. Current size: %.2f MB",
                            file.getSize() / (1024.0 * 1024.0))
            );
        }
        
        // Validate file extension
        String filename = file.getOriginalFilename();
        if (filename == null || !filename.contains(".")) {
            throw new FileUploadException("Invalid filename");
        }
        
        String extension = filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new FileUploadException(
                    String.format("Invalid file format. Allowed formats: %s", ALLOWED_EXTENSIONS)
            );
        }
        
        log.info("File validation passed: {} (Size: {} bytes)", filename, file.getSize());
    }
    
    /**
     * Call Flask ML API with the image file
     * 
     * PIPELINE DETAIL: Spring Boot → Flask API
     * 
     * This method handles the HTTP communication between Spring Boot and Flask:
     * 1. Wraps image file in multipart request
     * 2. Sends POST request to Flask API endpoint
     * 3. Receives base64 encoded overlay image
     * 4. Parses response into PredictionResponse DTO
     *
     * Request Details:
     * - Method: POST
     * - URL: http://127.0.0.1:5000/predict (from application.properties)
     * - Content-Type: multipart/form-data
     * - Body: file parameter with image
     * - Timeout: 10s (connect), 30s (read)
     *
     * Response Details:
     * Returns JSON:
     * {
     *   "success": true,
     *   "confidence": 85.5,
     *   "has_oil_spill": true,
     *   "overlay_image": "data:image/png;base64,...",
     *   "prediction_map": "data:image/png;base64,..."
     * }
     *
     * @param file MultipartFile to send to Flask
     * @return PredictionResponse parsed from Flask API response
     * @throws ApiException if Flask API call fails or returns error
     */
    private PredictionResponse callFlaskAPI(MultipartFile file) {
        try {
            // ========== STEP 1: Prepare Multipart Request ==========
            // Create a MultiValueMap to hold the file for multipart/form-data request
            // This is the same format as HTML form submission
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            
            // Add file to request body
            // Flask API expects parameter name "file"
            body.add("file", file.getResource());
            
            log.info("📤 Sending request to Flask API: {}", flaskApiUrl);
            log.info("   File: {} ({} bytes)", file.getOriginalFilename(), file.getSize());
            
            // ========== STEP 2: Send HTTP POST Request to Flask ==========
            // Uses RestTemplate configured in RestTemplateConfig
            // - Connection timeout: 10 seconds (time to establish connection)
            // - Read timeout: 30 seconds (time waiting for response)
            // 
            // Flask will:
            // 1. Receive image file
            // 2. Load model from model/oil_spill_model.keras
            // 3. Preprocess image:
            //    - Resize to 256x256
            //    - Normalize: divide by 255.0
            // 4. Run model.predict() to get prediction
            // 5. Apply threshold 0.3:
            //    - Values > 0.3 = oil spill (1)
            //    - Values <= 0.3 = no oil spill (0)
            // 6. Create overlay:
            //    - Load original image
            //    - Color detected regions RED ([255, 0, 0])
            //    - Use alpha blending for transparency
            // 7. Encode overlay as base64 PNG
            // 8. Return JSON response
            ResponseEntity<PredictionResponse> response = restTemplate.postForEntity(
                    flaskApiUrl,  // http://127.0.0.1:5000/predict
                    body,
                    PredictionResponse.class
            );
            
            // ========== STEP 3: Validate Flask Response ==========
            // Check HTTP status code
            if (response.getStatusCode() != HttpStatus.OK) {
                throw new ApiException(
                        "API_ERROR",
                        String.format("Flask API returned status %s", response.getStatusCode())
                );
            }
            
            log.info("✓ Response received from Flask API");
            log.info("   Status: {}", response.getStatusCode());
            
            // ========== STEP 4: Return PredictionResponse ==========
            // Response body is automatically deserialized from JSON to PredictionResponse DTO
            PredictionResponse predictions = response.getBody();
            
            if (predictions != null) {
                log.info("✓ Successfully parsed response:");
                log.info("   - Confidence: {}%", predictions.getConfidence());
                log.info("   - Oil Spill Detected: {}", predictions.getHasOilSpill());
                log.info("   - Overlay Image Size: {} bytes", 
                        (predictions.getOverlayImage() != null ? 
                            predictions.getOverlayImage().length() : 0));
            }
            
            return predictions;
            
        } catch (Exception e) {
            log.error("❌ Error calling Flask API: {}", e.getMessage(), e);
            log.error("   Make sure Flask API is running on port 5000");
            log.error("   Command: python ml_api.py");
            
            throw new ApiException(
                    "FLASK_API_ERROR",
                    "Failed to communicate with Flask API: " + e.getMessage(),
                    e
            );
        }
    }
    
    /**
     * Health check for ML API
     *
     * @return true if ML API is accessible
     */
    public boolean isMLAPIHealthy() {
        try {
            log.info("Checking ML API health...");
            ResponseEntity<String> response = restTemplate.getForEntity(
                    flaskApiUrl.replace("/predict", "/health"),
                    String.class
            );
            boolean healthy = response.getStatusCode() == HttpStatus.OK;
            log.info("ML API health check: {}", healthy ? "OK" : "FAILED");
            return healthy;
        } catch (Exception e) {
            log.error("ML API health check failed: {}", e.getMessage());
            return false;
        }
    }
}
