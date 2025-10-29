# Feathersense Dashboard

This project reads data from a Feathersense BLE sensor, writes it to InfluxDB, and visualizes it in Grafana.

## Setup

1. Install Docker and Docker Compose on your Raspberry Pi.
2. Clone this repository.
3. Build and run containers:

   ```bash
   docker-compose up --build -d

