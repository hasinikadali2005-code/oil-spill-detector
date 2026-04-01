#!/bin/bash
# Oil Spill Detection System - Startup Script
# This script starts both Flask ML API and Spring Boot backend

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    Oil Spill Detection System - Full Pipeline              ║"
echo "║                                                            ║"
echo "║  Frontend → Spring Boot Backend → Flask ML API → Model   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

# Get the project root directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📁 Project root: $PROJECT_ROOT"
echo

# ============================================================
# STEP 1: Start Flask ML API
# ============================================================
echo "1️⃣  Starting Flask ML API..."
echo "   Port: 5000"
echo "   URL: http://127.0.0.1:5000"
echo "   Endpoint: POST /predict"
echo
echo "   Requirements:"
echo "   - Python 3.8+"
echo "   - Keras, TensorFlow, OpenCV, NumPy"
echo
echo "   Starting..."
echo "   Command: python ml_api.py"
echo

# Start Flask in a new terminal (Windows)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start cmd /k "cd $PROJECT_ROOT && python ml_api.py"
else
    # Unix/Linux/Mac
    cd "$PROJECT_ROOT"
    python ml_api.py &
    FLASK_PID=$!
fi

# Wait for Flask to start
echo "⏳ Waiting for Flask API to start..."
sleep 5

# Check if Flask is running
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Flask ML API started successfully"
else
    echo "⚠️  Flask API may not have started. Check manually:"
    echo "   curl http://127.0.0.1:5000/health"
fi

echo

# ============================================================
# STEP 2: Start Spring Boot Backend
# ============================================================
echo "2️⃣  Starting Spring Boot Backend..."
echo "   Port: 8080"
echo "   URL: http://localhost:8080"
echo "   Endpoints:"
echo "   - POST /api/predict"
echo "   - GET /api/health"
echo
echo "   Requirements:"
echo "   - Java 17+"
echo "   - Maven 3.6+"
echo
echo "   Building and starting..."
echo "   Commands:"
echo "   - mvn clean install"
echo "   - mvn spring-boot:run"
echo

cd "$PROJECT_ROOT/spring-backend"

# Build project
echo "📦 Building Spring Boot project..."
mvn clean install -DskipTests > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed. Check Maven installation."
    exit 1
fi

# Start Spring Boot
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start cmd /k "mvn spring-boot:run"
else
    # Unix/Linux/Mac
    mvn spring-boot:run &
    SPRING_PID=$!
fi

echo "⏳ Waiting for Spring Boot to start..."
sleep 10

# Check if Spring Boot is running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Spring Boot Backend started successfully"
else
    echo "⚠️  Spring Boot may not have started. Check manually:"
    echo "   curl http://localhost:8080/api/health"
fi

echo

# ============================================================
# STEP 3: Instructions for Frontend
# ============================================================
echo "╔════════════════════════════════════════════════════════════╗"
echo "║            🎉 System Started Successfully! 🎉              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo
echo "✅ Flask ML API:      http://127.0.0.1:5000"
echo "✅ Spring Boot:       http://localhost:8080"
echo "✅ Frontend:          http://localhost:8080"
echo
echo "📝 Next Steps:"
echo "1. Open browser: http://localhost:8080"
echo "2. Upload a satellite image"
echo "3. Click 'Predict' button"
echo "4. View results with overlay image"
echo
echo "🧪 Test Health Endpoints:"
echo "   Flask:  curl http://127.0.0.1:5000/health"
echo "   Spring: curl http://localhost:8080/api/health"
echo
echo "📋 Architecture:"
echo "   Frontend → Spring Boot (8080) → Flask API (5000) → Model"
echo
echo "💾 Logs:"
echo "   Check console windows for detailed logs"
echo
echo "🛑 To Stop:"
echo "   Close the terminal windows or press Ctrl+C"
echo
echo "══════════════════════════════════════════════════════════════"

# Keep script running
if [[ ! "$OSTYPE" == "msys" && ! "$OSTYPE" == "cygwin" ]]; then
    wait
fi
