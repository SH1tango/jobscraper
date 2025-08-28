FROM ghcr.io/home-assistant/amd64-base-python:3.12-alpine

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

# Copy app
COPY api.py scraper.py scraper_config.yaml /app/
COPY run.sh /app/
RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]
