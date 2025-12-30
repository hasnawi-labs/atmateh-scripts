FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install requests

COPY substrate_sync_monitor.py .

RUN addgroup -S glokos && adduser -S glokos -G glokos

USER glokos

CMD ["python", "substrate_sync_monitor.py"]
