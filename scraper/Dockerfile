FROM ghcr.io/home-assistant/amd64-base:latest

RUN apk add --no-cache python3 py3-pip py3-virtualenv build-base

WORKDIR /app

# Install only what API needs
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt fastapi uvicorn

# Copy API only
COPY api.py /app/
COPY run.sh /app/
RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]
