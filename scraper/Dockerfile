ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.19
FROM ${BUILD_FROM}

# System deps for lxml
RUN apk add --no-cache python3 py3-pip libxml2 libxslt \
    && apk add --no-cache --virtual .build-deps gcc musl-dev libxml2-dev libxslt-dev

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy app files
COPY api.py scraper.py run.sh /app/
RUN chmod +x /app/run.sh

# Cleanup
RUN apk del .build-deps

EXPOSE 8001
ENV PYTHONUNBUFFERED=1
