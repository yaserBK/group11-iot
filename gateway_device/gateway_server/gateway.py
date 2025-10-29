import asyncio
from bleak import BleakClient, BleakScanner, BleakError

DEVICE_ADDRESS = "DA:19:2D:10:EE:86"
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify from device
UART_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write to device

def notification_handler(sender, data):
    """Called when new data is received from the device."""
    print(f"Received: {data.decode('utf-8').strip()}")

async def connect_and_listen():
    while True:
        try:
            print(f"Connecting to {DEVICE_ADDRESS}...")
            async with BleakClient(DEVICE_ADDRESS) as client:
                if await client.is_connected():
                    print("Connected successfully!")
                    
                    # Start listening for notifications
                    await client.start_notify(UART_RX_CHAR_UUID, notification_handler)
                    
                    # Keep the connection alive
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
