#!/bin/bash

set -e

echo "updating package lists..."
sudo apt update

echo "installing docker..."
sudo apt install -y docker.io

echo "Installing docker-compose..."
sudo apt install -y docker-compose

echo "adding user to docker group..."
sudo usermod -aG docker vagrant

echo "Installing make..."
sudo apt install -y make

echo "cloning the repository..."
rm -rf student-crud-api
git clone https://github.com/JayanthNaiduKundrapu/student-crud-api.git

echo "changing to the project directory..."
cd student-crud-api

echo "running docker-compose to set up the application..."
if docker ps -q -f name=student-api; then
    echo "application is already running. stopping the existing application..."
    make docker-compose-down
    echo "starting the application using docker-compose..."
    make docker-compose-up
else
    echo "starting the application using docker-compose..."
     make docker-compose-up
fi

echo "waiting for the application to start..."
sleep 10

echo "checking if the application is running..."
if curl -s http://localhost:8080/healthcheck | grep "healthy" > /dev/null; then
    echo "application is running successfully."
else
    echo "application is not running."
fi

echo "autorefreshing the shell..."
exec $SHELL -l

echo "provisioning complete."
