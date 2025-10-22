#!/bin/bash

echo "🍕 Starting All Food Delivery Services"
echo "====================================="

# Function to start service in background
start_service() {
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
    
    # Set Python path and start service
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
    python main.py &
    
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

# Start all services
start_service "auth-service" "8000"
start_service "catalog-service" "8002"
start_service "order-service" "8003"
start_service "payment-service" "8004"
start_service "restaurant-service" "8005"
start_service "dispatch-service" "8006"
start_service "notification-service" "8007"
start_service "reporting-service" "8008"

echo "🎉 All services started!"
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
echo "🛑 To stop all services:"
echo "   ./stop_all.sh"

