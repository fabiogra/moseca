# syntax=docker/dockerfile:1

FROM python:3.10


RUN apt-get update && \
    apt-get install -y ffmpeg jq curl && \
    pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ .
COPY app ./app
COPY img ./img

RUN wget --progress=bar:force:noscroll https://huggingface.co/fabiogra/baseline_vocal_remover/resolve/main/baseline.pth

RUN mkdir -p /tmp/ /tmp/vocal_remover /.cache /.config /tmp/htdemucs /tmp/htdemucs_6s && \
    chmod 777 /tmp /tmp/vocal_remover /.cache /.config /tmp/htdemucs /tmp/htdemucs_6s

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN chmod +x prepare_samples.sh

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health
RUN --mount=type=secret,id=PREPARE_SAMPLES,mode=0444 ./prepare_samples.sh

ENTRYPOINT ["streamlit", "run", "app/header.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
