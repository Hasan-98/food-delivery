#!/bin/bash

# Usage: ./run_service.sh <service-name>
# Example: ./run_service.sh auth-service

if [ $# -eq 0 ]; then
    echo "❌ Usage: ./run_service.sh <service-name>"
    echo ""
    echo "📋 Available services:"
    echo "   auth-service"
    echo "   catalog-service"
    echo "   order-service"
    echo "   payment-service"
    echo "   restaurant-service"
    echo "   dispatch-service"
    echo "   notification-service"
    echo "   reporting-service"
    echo ""
    echo "💡 Examples:"
    echo "   ./run_service.sh auth-service"
    echo "   ./run_service.sh catalog-service"
    exit 1
fi

SERVICE_NAME=$1

echo "🚀 Starting $SERVICE_NAME"
echo "========================="

# Check if service directory exists
if [ ! -d "$SERVICE_NAME" ]; then
    echo "❌ Service directory '$SERVICE_NAME' not found"
    exit 1
fi

cd $SERVICE_NAME

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/pyvenv.cfg" ] || [ ! -d "venv/lib" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Set Python path to include shared directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# Start the service
echo "🔄 Starting $SERVICE_NAME..."
echo "   Press Ctrl+C to stop"
echo ""

python main.py

