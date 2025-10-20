import os
import serial
from influxdb_client import InfluxDBClient, Point, WritePrecision

# UART device (Bluetooth RFCOMM)
UART_PORT = os.getenv("UART_PORT", "/dev/rfcomm0")
BAUD_RATE = int(os.getenv("BAUD_RATE", 9600))

# InfluxDB config
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "your_token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "your_org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "mybucket")

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=WritePrecision.NS)

# Connect to UART
ser = serial.Serial(UART_PORT, BAUD_RATE)
print(f"Listening on {UART_PORT} at {BAUD_RATE} baud")

while True:
    line = ser.readline().decode('utf-8').strip()
    print("Received:", line)
    try:
        value = float(line)  # Adjust parsing for your sensor
        point = Point("sensor_data").field("value", value)
        write_api.write(bucket=INFLUX_BUCKET, record=point)
    except ValueError:
        print(f"Could not convert '{line}' to float")
