package com.oilspill.exception;

/**
 * Custom exception for API-related errors
 * Thrown when communication with Flask ML API fails
 */
public class ApiException extends RuntimeException {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * Exception code for categorizing errors
     */
    private String code;
    
    /**
     * Constructor with message
     */
    public ApiException(String message) {
        super(message);
        this.code = "API_ERROR";
    }
    
    /**
     * Constructor with message and cause
     */
    public ApiException(String message, Throwable cause) {
        super(message, cause);
        this.code = "API_ERROR";
    }
    
    /**
     * Constructor with code and message
     */
    public ApiException(String code, String message) {
        super(message);
        this.code = code;
    }
    
    /**
     * Constructor with code, message, and cause
     */
    public ApiException(String code, String message, Throwable cause) {
        super(message, cause);
        this.code = code;
    }
    
    public String getCode() {
        return code;
    }
    
    public void setCode(String code) {
        this.code = code;
    }
}
