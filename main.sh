#!/bin/bash

# Import IMG_NAME from config.py
IMG_NAME=$(python3 -c "from config import get_img_name; print(get_img_name())")

# Build Docker image
docker build -t ${IMG_NAME} .

# Push Docker image
docker push ${IMG_NAME}

# Run Docker Compose
docker-compose -f compose.yaml up -d

# Check if the benchmark script ran successfully
if [ $? -ne 0 ]; then
    echo "Compose script failed. Stopping Docker containers..."
    docker-compose -f compose.yaml down
    exit 1
fi
# Optionally, you can add a cleanup step
# docker-compose -f compose.yaml down
