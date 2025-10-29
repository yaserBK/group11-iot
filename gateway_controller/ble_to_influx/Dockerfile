FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ble_to_influx.py .

CMD ["python3", "ble_to_influx.py"]

