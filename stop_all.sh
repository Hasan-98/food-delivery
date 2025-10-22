#!/bin/bash

echo "🛑 Stopping All Food Delivery Services"
echo "====================================="

# Function to stop service by PID file
stop_service() {
    local service_name=$1
    local pid_file="${service_name}_pid.txt"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat $pid_file)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo "✅ $service_name stopped (PID: $pid)"
        else
            echo "⚠️  $service_name was not running (PID: $pid)"
        fi
        rm $pid_file
    else
        echo "⚠️  No PID file found for $service_name"
    fi
}

# Stop all services
stop_service "auth-service"
stop_service "catalog-service"
stop_service "order-service"
stop_service "payment-service"
stop_service "restaurant-service"
stop_service "dispatch-service"
stop_service "notification-service"
stop_service "reporting-service"

echo ""
echo "🎉 All services stopped!"

