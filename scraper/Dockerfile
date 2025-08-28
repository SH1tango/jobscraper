# Use the standard Home Assistant base
FROM ghcr.io/home-assistant/amd64-base:latest

# Install Python and build tools
RUN apk add --no-cache python3 py3-pip py3-virtualenv build-base

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt fastapi uvicorn

# Copy app
COPY api.py scraper.py scraper_config.yaml /app/
COPY run.sh /app/
RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]
