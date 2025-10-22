#!/bin/bash

echo "🛑 Stopping All Food Delivery Services"
echo "====================================="

# Function to stop service by PID file
stop_service_by_pid() {
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
stop_service_by_pid "auth-service"
stop_service_by_pid "catalog-service"
stop_service_by_pid "order-service"
stop_service_by_pid "payment-service"
stop_service_by_pid "restaurant-service"
stop_service_by_pid "dispatch-service"
stop_service_by_pid "notification-service"
stop_service_by_pid "reporting-service"

echo ""
echo "🎉 All services stopped!"
echo ""
echo "💡 To start services again:"
echo "   ./start_services_fixed.sh"

