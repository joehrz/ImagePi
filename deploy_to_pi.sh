#!/bin/bash

# Define the Raspberry Pi credentials and destination
PI_USER="pi"
PI_HOST="raspberrypi.local"
PI_DIR="/home/pi/ImagePi"

# Create the directory on the Raspberry Pi
ssh ${PI_USER}@${PI_HOST} "mkdir -p ${PI_DIR}"

# Copy the Raspberry Pi code to the Raspberry Pi
scp -r raspberry_pi/* ${PI_USER}@${PI_HOST}:${PI_DIR}
