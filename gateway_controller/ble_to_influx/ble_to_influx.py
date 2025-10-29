import asyncio
from bleak import BleakClient, BleakError
from influxdb import InfluxDBClient
import os

# Bring the HCI interface up to ensure container has full control
os.system("hciconfig hci0 up")
# ------------------------
# BLE device info
# ------------------------
DEVICE_ADDRESS = "DA:19:2D:10:EE:86"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
EXPECTED_HANDSHAKE = "HANDSHAKE_GROUP11"
ACK_MESSAGE = "ACK_HANDSHAKE"

# ------------------------
# InfluxDB 1.8 info
# ------------------------
INFLUX_HOST = "influxdb"
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
handshake_verified = False
ble_client_global = None

async def send_ack():
    """Send ACK to sensor to complete handshake."""
    if ble_client_global:
        await ble_client_global.write_gatt_char(UART_RX_CHAR_UUID, (ACK_MESSAGE + "\r\n").encode("utf-8"))
        print("Sent ACK_HANDSHAKE to sensor")

def ble_notification_handler(sender, data):
    global handshake_verified
    message = data.decode("utf-8").strip()
    
    if not handshake_verified:
        if EXPECTED_HANDSHAKE in message:
            handshake_verified = True
            print("Handshake verified from sensor")
            asyncio.create_task(send_ack())  # send ACK back
        else:
            print(f"Ignoring unexpected handshake/data: {message}")
        return

    # Parse sensor data after handshake
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

# ------------------------
# BLE connect & listen loop
# ------------------------
async def connect_and_listen():
    global handshake_verified, ble_client_global
    while True:
        try:
            print(f"Connecting to {DEVICE_ADDRESS}...")
            async with BleakClient(DEVICE_ADDRESS) as ble_client:
                ble_client_global = ble_client
                connected_status = await ble_client.is_connected()
                if connected_status:
                    print("Connected successfully!")
                    handshake_verified = False  # reset handshake on new connection
                    await ble_client.start_notify(UART_RX_CHAR_UUID, ble_notification_handler)

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
# Main
# ------------------------
if __name__ == "__main__":
    asyncio.run(connect_and_listen())
