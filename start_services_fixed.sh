#!/bin/bash

echo "🍕 Starting Food Delivery Services (Fixed Import Issues)"
echo "======================================================"

# Function to start a service with proper Python path
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
    
    # Start the service with proper Python path
    echo "🔄 Starting $service_name..."
    PYTHONPATH="${PYTHONPATH}:$(pwd)/.." python main.py &
    
    # Store the PID
    echo $! > ../${service_name}_pid.txt
    
    # Wait a moment for service to start
    sleep 3
    
    # Check if service is running
    if curl -s http://localhost:$port/health > /dev/null; then
        echo "✅ $service_name is running on http://localhost:$port"
    else
        echo "❌ $service_name failed to start"
    fi
    
    cd ..
    echo ""
}

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start it first:"
    echo "   sudo systemctl start postgresql"
    echo "   createdb food_delivery"
    exit 1
fi
echo "✅ PostgreSQL is running"

# Check if RabbitMQ is running
echo "🔍 Checking RabbitMQ..."
if ! curl -s http://localhost:15672 > /dev/null 2>&1; then
    echo "❌ RabbitMQ is not running. Please start it first:"
    echo "   sudo systemctl start rabbitmq-server"
    exit 1
fi
echo "✅ RabbitMQ is running"

echo ""
echo "🚀 Starting all services..."
echo ""

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
echo "   ./stop_services_fixed.sh"
echo ""
echo "🔍 To check service status:"
echo "   ./check_services.sh"

