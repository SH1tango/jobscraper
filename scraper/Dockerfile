FROM ghcr.io/home-assistant/amd64-base:latest

RUN apk add --no-cache python3 py3-pip build-base

WORKDIR /app

# Create venv and install packages into it
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

# Copy API
COPY api.py run.sh /app/
RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]
