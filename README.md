# IoT Gateway Device

This repository sets up persistant containerized volumes for Grafana and InfluxDB, specifically for the ARM processor architecture on Raspberry Pi's running a 32Bit OS. The docker-compose.yml can be updated as necessary to enable one to prop-up these containers on a range of alternative hardware and operating systems.

Requirements:
1. Docker
2. Docker Compose
3. Python
4. A Raspberry Pi or any other wireless network capable computer. 

## Setup
### Grafana and Influx

Starting in the "gateway_controller/" directory: Build and run Grafana and InfluxDb Contaienrs by running the following command from the pojrect root

```bash
docker-compose up --build -d grafana influxdb
```
   
### The Gateway Reciever Script

1. Run the following commands in the "gateway_controller/" directory to create a python virtual environment on your device:

```bash
$ python3 -m venv .
$ source ./bin/activate   
```

5. Install necessary dependencies
```
$ pip install -r requirements.txt
```

6. Start the gateway controller script
```
python3 gateway_controller.py
```

Note: 
This code needs to be refactored if it is to scale beyond a single sensor. Here the sensor names are hardcoded into the controller script. 
It also does not currently have fault tolerance or the ability to reconnect to devices without being rerun. That said, the Grafana and Influx DB are set up with persitent volumes meaning that state will be conserved in the case the gateway disconnects from the sensor node. 



