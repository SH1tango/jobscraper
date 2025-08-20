# Use Home Assistant base image
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

# Install system dependencies for Python and lxml
RUN apk add --no-cache python3 py3-pip libxml2 libxslt && \
    apk add --no-cache --virtual .build-deps gcc musl-dev libxml2-dev libxslt-dev

# Create a virtual environment for Python packages
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Set workdir
WORKDIR /app

# Install Python dependencies inside the venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY api.py scraper.py run.sh ./
RUN chmod +x /app/run.sh

# Clean up build dependencies
RUN apk del .build-deps

# Expose port for API
EXPOSE 8001
ENV PYTHONUNBUFFERED=1

# Start the service
CMD ["/venv/bin/uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]

