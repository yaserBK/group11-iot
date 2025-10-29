import asyncio
from bleak import BleakClient, BleakError
from influxdb import InfluxDBClient

# ------------------------
# BLE device info
# ------------------------
DEVICE_ADDRESS = "DA:19:2D:10:EE:86"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# ------------------------
# InfluxDB 1.8 info
# ------------------------
INFLUX_HOST = "influxdb"       # Docker Compose service name
INFLUX_PORT = 8086
INFLUX_USER = "admin"
INFLUX_PASSWORD = "admin123"
INFLUX_DB = "sensor_data"

# ------------------------
# Setup InfluxDB client
# ------------------------
influx_client = InfluxDBClient(
    host=INFLUX_HOST,
    port=INFLUX_PORT,
    username=INFLUX_USER,
    password=INFLUX_PASSWORD,
    database=INFLUX_DB
)

# ------------------------
# BLE notification handler
# ------------------------
def notification_handler(sender, data):
    """Called when BLE device sends data."""
    try:
        message = data.decode("utf-8").strip()
        print(f"Received: {message}")

        # Assume CSV format: "pH,TDS,temperature,humidity,water_temp"
        values = message.split(",")
        if len(values) >= 5:
            pH = float(values[0])
            tds = float(values[1])
            temperature = float(values[2])
            humidity = float(values[3])
            water_temp = float(values[4])

            # Write to InfluxDB
            point = [{
                "measurement": "sensor_data",
                "fields": {
                    "pH": pH,
                    "TDS": tds,
                    "temperature": temperature,
                    "humidity": humidity,
                    "water_temp": water_temp
                }
            }]
            influx_client.write_points(point)
    except Exception as e:
        print(f"Error parsing/writing data: {e}")

# ------------------------
# BLE connect & listen loop
# ------------------------
async def connect_and_listen():
    while True:
        try:
            print(f"Connecting to {DEVICE_ADDRESS}...")
            async with BleakClient(DEVICE_ADDRESS) as ble_client:
                if await ble_client.is_connected():
                    print("Connected successfully!")
                    await ble_client.start_notify(UART_RX_CHAR_UUID, notification_handler)

                    # Keep connection alive
                    while await ble_client.is_connected():
                        await asyncio.sleep(1)

                    print("Device disconnected, retrying in 5s...")
                    await asyncio.sleep(5)

        except BleakError as e:
            print(f"BLE connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    asyncio.run(connect_and_listen())
