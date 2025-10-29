# Import the Adafruit Bluetooth library, part of Blinka.  Technical reference:
# https://circuitpython.readthedocs.io/projects/ble/en/latest/api.html

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from influxdb import InfluxDBClient


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

# ----------------------------------------------------------------
# Initialize global variables for the main loop.
ble = BLERadio()
uart_connection = None

# ----------------------------------------------------------------
# Begin the main processing loop.

while True:
    if not uart_connection:
        print("Trying to connect...")
        # Check for any device advertising services
        for adv in ble.start_scan(ProvideServicesAdvertisement):
            # Print name of the device
            name = adv.complete_name
            if name:
                print(name)
            # Print what services that are being advertised
            for svc in adv.services:
                print(str(svc))
            # Look for UART service and establish connection
            if UARTService in adv.services and adv.complete_name == "group11":
                uart_connection = ble.connect(adv)
                print("Connected")
                break
        ble.stop_scan()
    # Once connected start receiving data
    if uart_connection and uart_connection.connected:
        uart_service = uart_connection[UARTService]
        
        while uart_connection.connected:
            message = uart_service.readline().decode("utf-8").rstrip()
            try:
                values = message.split(",")
                if len(values) >= 5:
                    pH = float(values[1])
                    tds = float(values[2])
                    temperature = float(values[3])
                    humidity = float(values[4])
                    water_temp = float(values[5])

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
                print("Error Parsing Data")