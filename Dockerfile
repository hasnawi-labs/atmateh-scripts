FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install requests

COPY substrate_sync_monitor.py .

CMD ["python", "substrate_sync_monitor.py"]
