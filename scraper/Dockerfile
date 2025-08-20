FROM ghcr.io/home-assistant/amd64-base:latest

# Install system dependencies for lxml
RUN apk add --no-cache python3 py3-pip libxml2 libxslt && \
    apk add --no-cache --virtual .build-deps gcc musl-dev libxml2-dev libxslt-dev

WORKDIR /app

# Create a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy requirements and install into venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY api.py scraper.py /app/

# Clean up build deps
RUN apk del .build-deps

EXPOSE 8001

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
