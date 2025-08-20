# scraper/Dockerfile  ← ensure this is the file Supervisor builds
FROM ghcr.io/home-assistant/amd64-base:latest

# System deps for lxml
RUN apk add --no-cache python3 py3-pip libxml2 libxslt && \
    apk add --no-cache --virtual .build-deps gcc musl-dev libxml2-dev libxslt-dev

WORKDIR /app

# Create isolated venv and use it explicitly
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY api.py scraper.py /app/

# Clean build deps
RUN apk del .build-deps

EXPOSE 8001
CMD ["/venv/bin/uvicorn","api:app","--host","0.0.0.0","--port","8001"]
