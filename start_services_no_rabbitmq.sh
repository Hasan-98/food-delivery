#!/bin/bash

echo "🍕 Starting Services Without RabbitMQ (For Testing)"
echo "=================================================="

# Function to start service without RabbitMQ
start_service_simple() {
    local service_name=$1
    local port=$2
    
    echo "🚀 Starting $service_name on port $port..."
    
    cd $service_name
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment for $service_name..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "venv/pyvenv.cfg" ] || [ ! -d "venv/lib" ]; then
        echo "📥 Installing dependencies for $service_name..."
        pip install -r requirements.txt
    fi
    
    # Start the service without RabbitMQ
    echo "🔄 Starting $service_name (without RabbitMQ)..."
    PYTHONPATH="${PYTHONPATH}:$(pwd)/.." python main.py &
    
    # Store the PID
    echo $! > ../${service_name}_pid.txt
    
    # Wait a moment for service to start
    sleep 2
    
    # Check if service is running
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service_name is running on http://localhost:$port"
    else
        echo "⚠️  $service_name started but health check failed"
    fi
    
    cd ..
    echo ""
}

# Start services without RabbitMQ
start_service_simple "auth-service" "8000"
start_service_simple "catalog-service" "8002"
start_service_simple "order-service" "8003"
start_service_simple "payment-service" "8004"
start_service_simple "restaurant-service" "8005"
start_service_simple "dispatch-service" "8006"
start_service_simple "notification-service" "8007"
start_service_simple "reporting-service" "8008"

echo "🎉 All services started (without RabbitMQ)!"
echo ""
echo "📋 Service URLs:"
echo "   Auth Service:      http://localhost:8000"
echo "   Catalog Service:    http://localhost:8002"
echo "   Order Service:      http://localhost:8003"
echo "   Payment Service:    http://localhost:8004"
echo "   Restaurant Service: http://localhost:8005"
echo "   Dispatch Service:   http://localhost:8006"
echo "   Notification Service: http://localhost:8007"
echo "   Reporting Service:  http://localhost:8008"
echo ""
echo "⚠️  Note: Services are running without RabbitMQ"
echo "   Some features may not work (event-driven communication)"
echo "   For full functionality, start RabbitMQ or use Docker Compose"

