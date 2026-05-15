FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Hugging Face Spaces usa 7860 por padrão; docker-compose local sobrescreve para 8000
ENV PORT=7860

WORKDIR /app/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY requirements.docker.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.docker.txt

COPY . .

RUN pip install --no-cache-dir --no-deps -e .

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn beeai.api.main:app --host 0.0.0.0 --port ${PORT} --app-dir src"]
