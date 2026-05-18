FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Hugging Face Spaces usa 7860 por padrão; docker-compose local sobrescreve para 8000
ENV PORT=7860

WORKDIR /app/backend

COPY requirements.docker.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.docker.txt

COPY . .

RUN pip install --no-cache-dir --no-deps -e .

COPY start.sh ./
RUN chmod +x start.sh

EXPOSE ${PORT}

CMD ["./start.sh"]
