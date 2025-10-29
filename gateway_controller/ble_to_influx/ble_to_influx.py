import asyncio
import os
from bleak import BleakClient, BleakError
from influxdb import InfluxDBClient

# ------------------------
# Ensure BLE adapter is up
# ------------------------
os.system("hciconfig hci0 up")

# ------------------------
# BLE device info
# ------------------------
DEVICE_ADDRESS = "DA:19:2D:10:EE:86"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
EXPECTED_HANDSHAKE = "HANDSHAKE_GROUP11"
ACK_MESSAGE = "ACK_HANDSHAKE"

# ------------------------
# InfluxDB 1.8 info (host access)
# ------------------------
INFLUX_HOST = "localhost"  # host accesses Docker container via localhost
INFLUX_PORT = 8086
INFLUX_USER = "admin"
INFLUX_PASSWORD = "admin123"
INFLUX_DB = "sensor_data"

influxdb_client = InfluxDBClient(
    host=INFLUX_HOST,
    port=INFLUX_PORT,
    username=INFLUX_USER,
    password=INFLUX_PASSWORD,
    database=INFLUX_DB
)

# ------------------------
# BLE notification handler
# ------------------------
async def send_ack(ble_client):
    """Send ACK to sensor to complete handshake."""
    await ble_client.write_gatt_char(
        UART_RX_CHAR_UUID, (ACK_MESSAGE + "\r\n").encode("utf-8")
    )
    print("Sent ACK_HANDSHAKE to sensor")

def ble_notification_handler_factory(ble_client):
    """Factory to create a notification handler with handshake state."""
    handshake_verified = False

    def handler(sender, data):
        nonlocal handshake_verified
        message = data.decode("utf-8").strip()

        # --------------------
        # Handle handshake
        # --------------------
        if not handshake_verified:
            if EXPECTED_HANDSHAKE in message:
                handshake_verified = True
                print("Handshake verified from sensor")
                asyncio.create_task(send_ack(ble_client))
            else:
                print(f"Ignoring unexpected handshake/data: {message}")
            return

        # --------------------
        # Handle sensor data
        # --------------------
        try:
            values = message.split(",")
            if len(values) >= 5:
                pH = float(values[0])
                tds = float(values[1])
                temperature = float(values[2])
                humidity = float(values[3])
                water_temp = float(values[4])

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
                influxdb_client.write_points(point)
                print(f"Stored data: {message}")
        except Exception as e:
            print(f"Error parsing/writing data: {e}")

    return handler

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

                    # Reset handshake and assign handler
                    handler = ble_notification_handler_factory(ble_client)
                    await ble_client.start_notify(UART_RX_CHAR_UUID, handler)

                    # Keep connection alive
                    while await ble_client.is_connected():
                        await asyncio.sleep(1)

                    print("Device disconnected, retrying in 5 seconds...")
                    await asyncio.sleep(5)

        except BleakError as e:
            print(f"BLE connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

# ------------------------
# Main entry
# ------------------------
if __name__ == "__main__":
    asyncio.run(connect_and_listen())
