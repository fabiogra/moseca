# syntax=docker/dockerfile:1

FROM python:3.10

RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY img ./img
COPY app.py .

RUN mkdir -p /tmp /tmp/htdemucs /tmp/htdemucs_6s /.cache /.config && \
    chmod 777 /tmp /tmp/htdemucs /tmp/htdemucs_6s /.cache /.config

ENV PYTHONPATH="${PYTHONPATH}:/app"

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/ || exit 1

ENTRYPOINT ["python", "app.py"]
