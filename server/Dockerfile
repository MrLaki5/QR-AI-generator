FROM python:3.10.0-slim-buster

COPY server/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY server/ /app
COPY connection/ /app/connection

WORKDIR /app

ENTRYPOINT ["python", "server.py"]
