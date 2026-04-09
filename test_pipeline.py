#!/usr/bin/env python3
"""
Oil Spill Detection Pipeline - Test Suite
Tests each component of the complete pipeline
"""

import requests
import time
import sys
from pathlib import Path

# Configuration
FLASK_URL = "http://127.0.0.1:5000"
SPRING_URL = "http://localhost:8081"
FLASK_PREDICT = f"{FLASK_URL}/predict"
SPRING_PREDICT = f"{SPRING_URL}/api/predict"
FLASK_HEALTH = f"{FLASK_URL}/health"
SPRING_HEALTH = f"{SPRING_URL}/api/health"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print section header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def test_flask_health():
    """Test Flask API health endpoint"""
    print_header("TEST 1: Flask ML API Health Check")
    
    try:
        print_info(f"Checking Flask API: {FLASK_HEALTH}")
        response = requests.get(FLASK_HEALTH, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Flask API is running")
            print(f"  Status: {data.get('status')}")
            print(f"  Model Loaded: {data.get('model_loaded')}")
            print(f"  Model Path: {data.get('model_path')}")
            return True
        else:
            print_error(f"Flask returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to Flask API at {FLASK_URL}")
        print_warning("Make sure Flask is running: python ml_api.py")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_spring_health():
    """Test Spring Boot health endpoint"""
    print_header("TEST 2: Spring Boot Backend Health Check")
    
    try:
        print_info(f"Checking Spring Boot: {SPRING_HEALTH}")
        response = requests.get(SPRING_HEALTH, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Spring Boot is running")
            print(f"  Status: {data.get('status')}")
            print(f"  Service: {data.get('service')}")
            print(f"  ML API Status: {data.get('ml_api_status')}")
            
            if data.get('ml_api_status') == 'connected':
                print_success("Spring Boot is connected to Flask API")
                return True
            else:
                print_warning("Spring Boot cannot connect to Flask API")
                return False
        else:
            print_error(f"Spring Boot returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to Spring Boot at {SPRING_URL}")
        print_warning("Make sure Spring Boot is running: mvn spring-boot:run")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def create_test_image():
    """Create a simple test image"""
    print_info("Creating test image...")
    
    try:
        import numpy as np
        from PIL import Image
        
        # Create simple test image (256x256 with random noise)
        img_array = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        # Save to temporary location
        test_image_path = "/tmp/test_image.png" if sys.platform != "win32" else "test_image.png"
        img.save(test_image_path)
        
        print_success(f"Test image created: {test_image_path}")
        return test_image_path
        
    except ImportError:
        print_warning("PIL/Pillow not installed. Using sample approach.")
        return None

def test_flask_predict(image_path):
    """Test Flask predict endpoint"""
    print_header("TEST 3: Flask ML API Prediction")
    
    if not image_path:
        print_warning("Skipping Flask prediction test (no test image)")
        return False
    
    try:
        print_info(f"Sending image to Flask: {FLASK_PREDICT}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(FLASK_PREDICT, files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Flask prediction successful")
            print(f"  Success: {data.get('success')}")
            print(f"  Confidence: {data.get('confidence')}%")
            print(f"  Oil Spill Detected: {data.get('has_oil_spill')}")
            print(f"  Overlay Image: {len(data.get('overlay_image', ''))} bytes")
            return True
        else:
            print_error(f"Flask returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error during Flask prediction: {str(e)}")
        return False

def test_spring_predict(image_path):
    """Test Spring Boot predict endpoint"""
    print_header("TEST 4: Spring Boot Backend Prediction")
    
    if not image_path:
        print_warning("Skipping Spring Boot prediction test (no test image)")
        return False
    
    try:
        print_info(f"Sending image to Spring Boot: {SPRING_PREDICT}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(SPRING_PREDICT, files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Spring Boot prediction successful")
            print(f"  Success: {data.get('success')}")
            print(f"  Confidence: {data.get('confidence')}%")
            print(f"  Oil Spill Detected: {data.get('has_oil_spill')}")
            print(f"  Overlay Image: {len(data.get('overlay_image', ''))} bytes")
            return True
        else:
            print_error(f"Spring Boot returned status {response.status_code}")
            print_error(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print_error(f"Error during Spring Boot prediction: {str(e)}")
        return False

def test_frontend_access():
    """Test frontend access"""
    print_header("TEST 5: Frontend Access")
    
    try:
        print_info(f"Testing frontend access: {SPRING_URL}/")
        response = requests.get(f"{SPRING_URL}/", timeout=5)
        
        if response.status_code == 200:
            if 'Oil Spill' in response.text or 'html' in response.text:
                print_success(f"Frontend is accessible")
                print_info(f"Open in browser: {SPRING_URL}/")
                return True
            else:
                print_warning("Frontend page may not be correct HTML")
                return False
        else:
            print_error(f"Frontend returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error accessing frontend: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{BOLD}{BLUE}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║  Oil Spill Detection Pipeline - Test Suite             ║")
    print("█  Testing complete system: Frontend → Spring → Flask   ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(RESET)
    
    results = {}
    
    # Test 1: Flask Health
    results['Flask Health'] = test_flask_health()
    time.sleep(1)
    
    # Test 2: Spring Boot Health
    results['Spring Boot Health'] = test_spring_health()
    time.sleep(1)
    
    # Test 3: Frontend
    results['Frontend Access'] = test_frontend_access()
    time.sleep(1)
    
    # Create test image for predictions
    test_image = create_test_image()
    time.sleep(1)
    
    # Test 4: Flask Prediction
    results['Flask Prediction'] = test_flask_predict(test_image)
    time.sleep(1)
    
    # Test 5: Spring Boot Prediction
    results['Spring Boot Prediction'] = test_spring_predict(test_image)
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BOLD}Total: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print_success("All tests passed! System is ready.")
        print_info("Open browser: http://localhost:8081")
        return True
    else:
        print_error("Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
