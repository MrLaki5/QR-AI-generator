FROM python:3.10.0-slim-buster

COPY worker/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN pip install --upgrade diffusers[torch]
RUN pip install transformers accelerate xformers

COPY worker/ /app
COPY connection/ /app/connection

WORKDIR /app

ENTRYPOINT ["python", "worker.py"]
