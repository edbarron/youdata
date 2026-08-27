FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# (Si usas numpy/pandas que compilen, descomenta estas 3 líneas)
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Sugerencia: permite configurar la ruta de la DB por env (opcional)
# ENV DB_PATH=youdata.db

CMD ["python", "main.py"]
