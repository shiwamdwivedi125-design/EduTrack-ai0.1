FROM node:20-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=10000

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/ml_models ./ml_models
COPY scripts ./scripts
COPY data ./data
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html
COPY deploy/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY deploy/supervisord.conf /etc/supervisor/conf.d/edutrack.conf
COPY deploy/entrypoint.sh /usr/local/bin/edutrack-entrypoint
RUN chmod +x /usr/local/bin/edutrack-entrypoint

EXPOSE 10000

ENTRYPOINT ["/usr/local/bin/edutrack-entrypoint"]
