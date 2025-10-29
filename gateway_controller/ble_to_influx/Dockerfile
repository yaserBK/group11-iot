FROM --platform=linux/arm/v7 python:3.11-slim-bullseye

# Install system dependencies for BLE + building Python packages
RUN apt-get update && apt-get install -y \
    bluez \
    libbluetooth-dev \
    libglib2.0-dev \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ble_to_influx.py .

CMD ["python", "ble_to_influx.py"]
