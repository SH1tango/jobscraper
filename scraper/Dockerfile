# Use the supported Python base for add-ons
FROM ghcr.io/home-assistant/amd64-base-python:3.11

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

# Copy app files
COPY api.py scraper.py scraper_config.yaml /app/
COPY run.sh /app/
RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]
