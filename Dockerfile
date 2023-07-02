# syntax=docker/dockerfile:1

FROM python:3.8


RUN apt-get update && \
    apt-get install -y ffmpeg jq curl && \
    pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ .
COPY app ./app
copy img ./img

RUN wget --progress=bar:force:noscroll https://huggingface.co/fabiogra/baseline_vocal_remover/resolve/main/baseline.pth

RUN mkdir -p /tmp/ /tmp/vocal_remover /.cache /.config && \
    chmod 777 /tmp /tmp/vocal_remover /.cache /.config

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN chmod +x prepare_samples.sh

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

RUN ["./prepare_samples.sh"]

ENTRYPOINT ["streamlit", "run", "app/header.py", "--server.port=7860", "--server.address=0.0.0.0"]
