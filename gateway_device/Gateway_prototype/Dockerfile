# Use an official Python runtime as a parent image
# This will automatically pull the correct ARM-architecture image on your Pi
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for BLE on Linux
# - bluez: The official Linux Bluetooth protocol stack
# - dbus: Used for inter-process communication (how bleak talks to bluez)
RUN apt-get update && apt-get install -y \
    bluez \
    dbus \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the listener script into the container
COPY ble_listener.py .

# Run the script when the container launches
CMD ["python", "-u", "ble_listener.py"]