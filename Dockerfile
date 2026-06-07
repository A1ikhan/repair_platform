FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files — dummy key is safe here (only used by collectstatic, not runtime)
RUN SECRET_KEY=build-only-dummy-key python manage.py collectstatic --noinput

RUN mkdir -p /app/staticfiles /tmp/prometheus_multiproc

EXPOSE 8080

CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8080 core.asgi:application"]