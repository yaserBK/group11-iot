import asyncio
from bleak import BleakClient, BleakError
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# BLE device info
DEVICE_ADDRESS = "DA:19:2D:10:EE:86"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# InfluxDB info
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "admin123"
INFLUX_ORG = "group11_org"
INFLUX_BUCKET = "group11_bucket"

# Setup InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def notification_handler(sender, data):
    """Called when BLE device sends data."""
    try:
        message = data.decode("utf-8").strip()
        print(f"Received: {message}")

        # Assume CSV format from your Feathersense: "temperature,humidity"
        values = message.split(",")
        if len(values) >= 2:
            temperature = float(values[0])
            humidity = float(values[1])

            # Write to InfluxDB
            point = (
                Point("sensor_data")
                .field("temperature", temperature)
                .field("humidity", humidity)
            )
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    except Exception as e:
        print(f"Error parsing/writing data: {e}")

async def connect_and_listen():
    while True:
        try:
            print(f"Connecting to {DEVICE_ADDRESS}...")
            async with BleakClient(DEVICE_ADDRESS) as client:
                if await client.is_connected():
                    print("Connected successfully!")
                    await client.start_notify(UART_RX_CHAR_UUID, notification_handler)
                    while await client.is_connected():
                        await asyncio.sleep(1)
                    print("Device disconnected, retrying...")
        except BleakError as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect_and_listen())

