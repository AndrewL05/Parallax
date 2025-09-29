#!/bin/bash

# Docker build script for Parallax app
set -e

echo "🚀 Building Parallax Docker containers..."

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
BUILD_TYPE=${2:-normal}

print_status "Building for environment: $ENVIRONMENT"
print_status "Build type: $BUILD_TYPE"

# Build based on environment
case $ENVIRONMENT in
    "development"|"dev")
        print_status "Building development containers..."
        docker-compose build
        ;;
    "production"|"prod")
        print_status "Building production containers..."
        if [ "$BUILD_TYPE" = "optimized" ]; then
            print_status "Using optimized production Dockerfiles..."
            docker build -f backend/Dockerfile.prod -t parallax-backend:prod backend/
            docker build -f frontend/Dockerfile.prod -t parallax-frontend:prod frontend/
        else
            docker-compose -f docker-compose.prod.yml build
        fi
        ;;
    *)
        print_error "Invalid environment. Use 'development' or 'production'"
        exit 1
        ;;
esac

print_status "✅ Build completed successfully!"

# Show built images
print_status "Built images:"
docker images | grep parallax