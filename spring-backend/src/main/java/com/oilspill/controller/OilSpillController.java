package com.oilspill.controller;

import com.oilspill.dto.PredictionResponse;
import com.oilspill.exception.ApiException;
import com.oilspill.exception.FileUploadException;
import com.oilspill.service.OilSpillService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

/**
 * REST Controller for Oil Spill Detection API
 * Handles HTTP requests for image upload and prediction
 */
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*", maxAge = 3600)
public class OilSpillController {
    private static final Logger log = LoggerFactory.getLogger(OilSpillController.class);
    
    @Autowired
    private OilSpillService oilSpillService;
    
    /**
     * PIPELINE STEP 1: Upload image and predict oil spill
     * 
     * This is the main REST endpoint that initiates the complete pipeline:
     * Frontend → Spring Boot → Flask API → Spring Boot → Frontend
     *
     * Complete Request/Response Flow:
     * 
     * 1. FRONTEND SENDS REQUEST:
     *    - Browser fetch API makes POST request
     *    - Endpoint: http://localhost:8080/api/predict
     *    - Content-Type: multipart/form-data
     *    - Body: file parameter with image
     *    - Code location: spring-backend/src/main/resources/static/index.html:407-430
     *
     * 2. SPRING BOOT RECEIVES REQUEST:
     *    - Controller method receives MultipartFile parameter
     *    - CORS enabled to allow frontend requests
     *    - Request validation done by Spring Framework
     *
     * 3. BUSINESS LOGIC (OilSpillService):
     *    - Calls predictOilSpill() method
     *    - Validates file (type, size, extension)
     *    - Calls Flask API with file
     *    - Returns PredictionResponse with results
     *
     * 4. SPRING BOOT SENDS RESPONSE:
     *    - PredictionResponse converted to JSON
     *    - HTTP 200 OK with JSON body
     *    - Example response:
     *    {
     *      "success": true,
     *      "confidence": 85.5,
     *      "has_oil_spill": true,
     *      "overlay_image": "data:image/png;base64,iVBORw0KGgo...",
     *      "prediction_map": "data:image/png;base64,iVBORw0KGgo..."
     *    }
     *
     * 5. FRONTEND RECEIVES RESPONSE:
     *    - JavaScript parses JSON
     *    - Sets <img src="data:image/png;base64,...">
     *    - Displays confidence percentage and status
     *    - Shows success message
     *    - Code location: spring-backend/src/main/resources/static/index.html:435-460
     *
     * Error Handling:
     * - 400 Bad Request: Invalid file (extension, size, empty)
     * - 500 Internal Server Error: Flask API error or unexpected error
     * - Detailed error response with error_code and error message
     *
     * @param file Image file to analyze (uploaded from frontend)
     * @return ResponseEntity with PredictionResponse (JSON) on success
     *         or error response (JSON) on failure
     * @status 200 OK - Prediction successful
     * @status 400 Bad Request - Invalid file
     * @status 500 Internal Server Error - Server/API error
     */
    @PostMapping("/predict")
    public ResponseEntity<?> predictOilSpill(@RequestParam("file") MultipartFile file) {
        try {
            log.info("═══════════════════════════════════════════════════════");
            log.info("PIPELINE INITIATED: Frontend Request Received");
            log.info("═══════════════════════════════════════════════════════");
            log.info("📥 Received image upload request");
            log.info("   Filename: {}", file.getOriginalFilename());
            log.info("   Size: {} bytes", file.getSize());
            log.info("   Content-Type: {}", file.getContentType());
            
            // ========== STEP 1: Call Service to Process Image ==========
            // OilSpillService handles:
            // 1. File validation
            // 2. Forwarding to Flask API
            // 3. Receiving and parsing response
            log.info("\n📤 Forwarding to OilSpillService for processing...");
            PredictionResponse response = oilSpillService.predictOilSpill(file);
            
            // ========== STEP 2: Return Success Response to Frontend ==========
            // Jackson automatically converts PredictionResponse to JSON
            log.info("\n✓ Returning prediction response to frontend as JSON");
            log.info("   Response includes:");
            log.info("   - overlay_image: base64 encoded PNG with RED highlights");
            log.info("   - prediction_map: base64 encoded prediction mask");
            log.info("   - confidence: prediction confidence percentage");
            log.info("   - has_oil_spill: boolean indicating detection");
            
            log.info("\n═══════════════════════════════════════════════════════");
            log.info("✓ PIPELINE COMPLETED SUCCESSFULLY");
            log.info("═══════════════════════════════════════════════════════\n");
            
            return ResponseEntity.ok(response);
            
        } catch (FileUploadException e) {
            // ========== ERROR: File Validation Failed ==========
            // Bad Request - Client error
            // Returns HTTP 400 with error details
            log.error("\n✗ FILE UPLOAD ERROR ✗");
            log.error("   Error: {}", e.getMessage());
            log.error("   Code: FILE_ERROR");
            log.error("   HTTP Status: 400 Bad Request");
            log.error("   Return: {\"success\": false, \"error_code\": \"FILE_ERROR\", ...}\n");
            
            return ResponseEntity
                    .status(HttpStatus.BAD_REQUEST)
                    .body(createErrorResponse("FILE_ERROR", e.getMessage()));
                    
        } catch (ApiException e) {
            // ========== ERROR: Flask API Communication Failed ==========
            // Internal Server Error - Server error
            // Returns HTTP 500 with error details
            log.error("\n✗ FLASK API ERROR ✗");
            log.error("   Error: {}", e.getMessage());
            log.error("   Code: {}", e.getCode());
            log.error("   HTTP Status: 500 Internal Server Error");
            log.error("   Possible Causes:");
            log.error("   - Flask API not running on port 5000");
            log.error("   - Model file not found: model/oil_spill_model.keras");
            log.error("   - Network connectivity issue");
            log.error("   Action: Start Flask API with: python ml_api.py\n");
            
            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse(e.getCode(), e.getMessage()));
                    
        } catch (Exception e) {
            // ========== ERROR: Unexpected Error ==========
            // Internal Server Error - Server error
            // Returns HTTP 500 with generic error message
            log.error("\n✗ UNEXPECTED ERROR ✗");
            log.error("   Error: {}", e.getMessage());
            log.error("   HTTP Status: 500 Internal Server Error");
            log.error("   Stack Trace:", e);
            
            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("INTERNAL_ERROR", "An unexpected error occurred"));
        }
    }
    
    /**
     * Health check endpoint
     * Verifies if the service is running and ML API is accessible
     * 
     * @return Health status
     * @status 200 OK - Service is healthy
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        try {
            boolean mlAPIHealthy = oilSpillService.isMLAPIHealthy();
            
            Map<String, Object> health = new HashMap<>();
            health.put("status", "healthy");
            health.put("service", "Oil Spill Detection API");
            health.put("ml_api_status", mlAPIHealthy ? "connected" : "disconnected");
            
            return ResponseEntity.ok(health);
            
        } catch (Exception e) {
            log.error("Health check error: {}", e.getMessage());
            return ResponseEntity
                    .status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(createErrorResponse("HEALTH_CHECK_ERROR", "Service unavailable"));
        }
    }
    
    /**
     * Create error response object
     * 
     * @param code Error code
     * @param message Error message
     * @return Error response map
     */
    private Map<String, Object> createErrorResponse(String code, String message) {
        Map<String, Object> error = new HashMap<>();
        error.put("success", false);
        error.put("error_code", code);
        error.put("error", message);
        return error;
    }
}
