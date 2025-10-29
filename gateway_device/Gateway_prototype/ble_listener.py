import asyncio
import sys
import os
from bleak import BleakClient, BleakScanner
from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

# --- Configuration ---
DEVICE_NAME = "group11"
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# These are the field names for your data, in the order they appear in the CSV
# Make sure this matches the data from your FeatherSense!
FIELD_NAMES = ["co2", "light", "humidity", "soil_moisture", "soil_ph"]

# --- InfluxDB Configuration (from Environment Variables) ---
INFLUX_URL = os.environ.get("INFLUXDB_URL")
INFLUX_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUX_ORG = os.environ.get("INFLUXDB_ORG")
INFLUX_BUCKET = os.environ.get("INFLUXDB_BUCKET")

# --- Globals for Influx client ---
influx_client: InfluxDBClientAsync | None = None
influx_write_api = None

async def notification_handler(sender, data):
    """Callback for when data is received from the device."""
    global influx_write_api, INFLUX_ORG, INFLUX_BUCKET
    
    try:
        message = data.decode("utf-8").strip()
        print(f"Received: {message}")

        # 1. Parse the CSV data
        values = message.split(',')
        if len(values) != len(FIELD_NAMES):
            print(f"  [WARN] Mismatched data. Expected {len(FIELD_NAMES)} fields, got {len(values)}")
            return

        # 2. Create an InfluxDB Point
        point = Point("sensors").tag("source", "feathersense")
        
        # 3. Add all fields from the CSV
        for i, name in enumerate(FIELD_NAMES):
            try:
                # Convert all values to float for storage
                field_value = float(values[i])
                point.field(name, field_value)
            except ValueError:
                print(f"  [WARN] Could not parse field '{name}' (value: '{values[i]}') as float.")
                # Skip this field but continue
        
        # 4. Write the point to InfluxDB
        if influx_write_api:
            await influx_write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print("  -> Written to InfluxDB")

    except Exception as e:
        print(f"[ERROR] in notification_handler: {e}")


async def main():
    """Main function to scan, connect, listen, and write to InfluxDB."""
    global influx_client, influx_write_api

    # --- Check for InfluxDB credentials ---
    if not all([INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET]):
        print("Error: InfluxDB environment variables not set.")
        print("INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET")
        sys.exit(1)

    try:
        # --- Connect to InfluxDB ---
        print(f"Connecting to InfluxDB at {INFLUX_URL}...")
        influx_client = InfluxDBClientAsync(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        health = await influx_client.health()
        if health.status != "pass":
            raise Exception(f"InfluxDB health check failed: {health.message}")
        
        # Create the ASYNC write API
        influx_write_api = influx_client.write_api()
        print("InfluxDB connection successful.")

        # --- Connect to BLE Device ---
        device = None
        print(f"Scanning for device named '{DEVICE_NAME}'...")
        async with BleakScanner() as scanner:
            device = await scanner.find_device_by_name(DEVICE_NAME)

        if device is None:
            print(f"Error: Could not find device '{DEVICE_NAME}'.")
            sys.exit(1)

        print(f"Found device: {device.name} ({device.address})")

        async with BleakClient(device) as client:
            if not client.is_connected:
                print("Error: Failed to connect.")
                sys.exit(1)
            
            print(f"Successfully connected to {DEVICE_NAME}")

            await client.start_notify(UART_TX_CHAR_UUID, notification_handler)
            print("Notifications enabled. Waiting for data...")
            print("Press Ctrl+C to stop.")
            
            await asyncio.Event().wait() # Keep script alive

    except asyncio.CancelledError:
        print("Stop signal received. Shutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # --- Clean up ---
        if influx_write_api:
            await influx_write_api.close()
        if influx_client:
            await influx_client.close()
        print("InfluxDB client closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")