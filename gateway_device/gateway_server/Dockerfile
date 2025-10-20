FROM python:3.12-slim

# Installing Dependencies
RUN pip install pyserial influxdb-client

# non-root user
RUN useradd -ms /bin/bash appuser
USER appuser
WORKDIR /home/appuser

COPY gateway.py .

CMD ["python", "gateway.py"]
