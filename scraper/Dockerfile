FROM ghcr.io/home-assistant/amd64-base-python:3.12-alpine

# Install uvicorn & fastapi
RUN pip install --no-cache-dir fastapi uvicorn

# Copy your script
WORKDIR /app
COPY api.py /app/

# Run script via run.sh
COPY run.sh /app/
RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]
