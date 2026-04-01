FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY crontab.txt /etc/cron.d/updater-job

RUN chmod 0644 /etc/cron.d/updater-job && crontab /etc/cron.d/updater-job
RUN mkdir -p /var/log/rag-updater

CMD ["cron", "-f"]