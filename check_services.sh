#!/bin/bash

echo "🔍 Checking Food Delivery Services Status"
echo "========================================="

# Function to check service status
check_service() {
    local service_name=$1
    local port=$2
    local url="http://localhost:$port/health"
    
    echo -n "🔍 $service_name (port $port): "
    
    if curl -s $url > /dev/null 2>&1; then
        echo "✅ Running"
    else
        echo "❌ Not running"
    fi
}

echo ""
echo "📊 Service Status:"
echo ""

# Check all services
check_service "Auth Service" "8000"
check_service "Catalog Service" "8002"
check_service "Order Service" "8003"
check_service "Payment Service" "8004"
check_service "Restaurant Service" "8005"
check_service "Dispatch Service" "8006"
check_service "Notification Service" "8007"
check_service "Reporting Service" "8008"

echo ""
echo "🏥 Infrastructure Status:"
echo ""

# Check PostgreSQL
echo -n "🔍 PostgreSQL (port 5432): "
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

# Check RabbitMQ
echo -n "🔍 RabbitMQ (port 5672): "
if curl -s http://localhost:15672 > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

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
echo "📚 API Documentation:"
echo "   Auth:      http://localhost:8000/docs"
echo "   Catalog:   http://localhost:8002/docs"
echo "   Order:     http://localhost:8003/docs"
echo "   Payment:   http://localhost:8004/docs"
echo "   Restaurant: http://localhost:8005/docs"
echo "   Dispatch:  http://localhost:8006/docs"
echo "   Notification: http://localhost:8007/docs"
echo "   Reporting: http://localhost:8008/docs"
