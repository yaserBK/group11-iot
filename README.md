# IoT Gateway Device

This repository sets up persistant containerized volumes for Grafana and InfluxDB, specifically for the ARM processor architecture on Raspberry Pi's running a 32Bit OS. The docker-compose.yml can be updated as necessary to enable one to prop-up these containers on a range of alternative hardware and operating systems.




## Setup
### Grafana and Influx

1. Install Docker and Docker Compose on your Raspberry Pi.
2. Clone this repository.
3. Build and run Grafana and InfluxDb Contaienrs by running the following command from the pojrect root

   ```bash
   docker-compose up --build -d grafana influxdb
   ```
   
### The Gateway Reciever Script

1. Navigate into the ble_to_influx directory and run the following commands:

```bash
$ python3 -m venv .
$ source ./bin/activate   
```

5. Install necessary dependencies by running 
```
$ pip install -r requirements.txt
```

6. Finally, start the gateway controller script:
```
python3 ble_to_influx2.py
```

Note: 
This code needs to be refactored if it is to scale beyond a single sensor. Here the sensor names are hardcoded into the controller script. 
It also does not currently have fault tolerance or the ability to reconnect to devices without being rerun. That said, the Grafana and Influx DB are set up with persitent volumes meaning that state will be conserved in the case the gateway disconnects from the sensor node. 



