package com.oilspill.exception;

/**
 * Exception thrown when file upload validation fails
 */
public class FileUploadException extends RuntimeException {
    
    private static final long serialVersionUID = 1L;
    
    public FileUploadException(String message) {
        super(message);
    }
    
    public FileUploadException(String message, Throwable cause) {
        super(message, cause);
    }
}
