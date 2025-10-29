# Feathersense Dashboard

This project reads data from a Feathersense BLE sensor, writes it to InfluxDB, and visualizes it in Grafana.

## Setup

1. Install Docker and Docker Compose on your Raspberry Pi.
2. Clone this repository.
3. Build and run Grafana and InfluxDb Contaienrs

   ```bash
   docker-compose up --build -d grafana influxdb
   ```

4. Create a python venv on your raspberry pi by running the following commands in your project root:

```bash
$ python3 -m venv .
$ source ./bin/activate   
```

5. Next, instally necessary dependencies by running
```
$ pip install -r requirements.txt
```

6. Finally, start the gateway controller script:
```
python3 gateway_controller/ble_to_influx/blew_to_influx2.py
```

Note: 
This code needs to be refactored if it is to scale beyond a single sensor. Here the sensor names are hardcoded into the controller script. 
It also does not currently have fault tolerance or the ability to reconnect to devices without being rerun. That said, the Grafana and Influx DB are set up with persitent volumes meaning that state will be conserved in the case the gateway disconnects from the sensor node. 



