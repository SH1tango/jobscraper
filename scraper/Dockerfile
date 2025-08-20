FROM ghcr.io/home-assistant/amd64-base:latest

# system deps
RUN apk add --no-cache python3 py3-pip libxml2 libxslt \
 && apk add --no-cache --virtual .build-deps gcc musl-dev libxml2-dev libxslt-dev

WORKDIR /app

# venv
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# deps
COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# app
COPY api.py scraper.py /app/

# s6 scripts
COPY rootfs/ /               # copies cont-init and services.d into place

# cleanup
RUN apk del .build-deps

EXPOSE 8001
