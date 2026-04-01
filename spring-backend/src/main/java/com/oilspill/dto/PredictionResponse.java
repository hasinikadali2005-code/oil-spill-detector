package com.oilspill.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Data Transfer Object for Prediction Response
 * Represents the response from the Flask ML API
 */
public class PredictionResponse {
    
    /**
     * Indicates if the prediction was successful
     */
    @JsonProperty("success")
    private Boolean success;
    
    /**
     * Confidence level of the prediction (0-100)
     */
    @JsonProperty("confidence")
    private Double confidence;
    
    /**
     * Whether oil spill was detected
     */
    @JsonProperty("has_oil_spill")
    private Boolean hasOilSpill;
    
    /**
     * Base64 encoded overlay image with detected regions highlighted
     */
    @JsonProperty("overlay_image")
    private String overlayImage;
    
    /**
     * Base64 encoded prediction mask
     */
    @JsonProperty("prediction_map")
    private String predictionMap;
    
    /**
     * Error message if prediction failed
     */
    @JsonProperty("error")
    private String error;

    public PredictionResponse() {
    }

    public PredictionResponse(Boolean success, Double confidence, Boolean hasOilSpill, String overlayImage, String predictionMap, String error) {
        this.success = success;
        this.confidence = confidence;
        this.hasOilSpill = hasOilSpill;
        this.overlayImage = overlayImage;
        this.predictionMap = predictionMap;
        this.error = error;
    }

    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public Double getConfidence() {
        return confidence;
    }

    public void setConfidence(Double confidence) {
        this.confidence = confidence;
    }

    public Boolean getHasOilSpill() {
        return hasOilSpill;
    }

    public void setHasOilSpill(Boolean hasOilSpill) {
        this.hasOilSpill = hasOilSpill;
    }

    public String getOverlayImage() {
        return overlayImage;
    }

    public void setOverlayImage(String overlayImage) {
        this.overlayImage = overlayImage;
    }

    public String getPredictionMap() {
        return predictionMap;
    }

    public void setPredictionMap(String predictionMap) {
        this.predictionMap = predictionMap;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}
