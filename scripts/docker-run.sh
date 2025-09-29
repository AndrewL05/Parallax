#!/bin/bash

# Docker run script for Parallax app
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Parse command line arguments
ENVIRONMENT=${1:-development}
ACTION=${2:-up}

print_status "Environment: $ENVIRONMENT"
print_status "Action: $ACTION"

# Function to check if .env files exist
check_env_files() {
    if [ ! -f "backend/.env" ]; then
        print_warning "backend/.env file not found. Creating template..."
        cat > backend/.env << EOF
# MongoDB Configuration
MONGODB_URL=mongodb://admin:password@mongodb:27017/parallax?authSource=admin

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Application Configuration
SECRET_KEY=your_secret_key_here
DEBUG=False
EOF
        print_warning "Please update backend/.env with your actual values"
    fi
}

# Run based on environment and action
case $ENVIRONMENT in
    "development"|"dev")
        check_env_files
        case $ACTION in
            "up")
                print_status "Starting development environment..."
                docker-compose up -d
                ;;
            "down")
                print_status "Stopping development environment..."
                docker-compose down
                ;;
            "logs")
                print_status "Showing logs..."
                docker-compose logs -f
                ;;
            "restart")
                print_status "Restarting development environment..."
                docker-compose restart
                ;;
            *)
                print_error "Invalid action. Use 'up', 'down', 'logs', or 'restart'"
                exit 1
                ;;
        esac
        ;;
    "production"|"prod")
        case $ACTION in
            "up")
                print_status "Starting production environment..."
                docker-compose -f docker-compose.prod.yml up -d
                ;;
            "down")
                print_status "Stopping production environment..."
                docker-compose -f docker-compose.prod.yml down
                ;;
            "logs")
                print_status "Showing logs..."
                docker-compose -f docker-compose.prod.yml logs -f
                ;;
            "restart")
                print_status "Restarting production environment..."
                docker-compose -f docker-compose.prod.yml restart
                ;;
            *)
                print_error "Invalid action. Use 'up', 'down', 'logs', or 'restart'"
                exit 1
                ;;
        esac
        ;;
    *)
        print_error "Invalid environment. Use 'development' or 'production'"
        exit 1
        ;;
esac

if [ "$ACTION" = "up" ]; then
    print_status "✅ Containers started successfully!"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend API: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"

    print_status "Container status:"
    if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml ps
    else
        docker-compose ps
    fi
fi