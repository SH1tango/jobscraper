FROM ghcr.io/home-assistant/amd64-base:latest

# Install Python + build deps
RUN apk add --no-cache python3 py3-pip build-base

WORKDIR /app

# Create venv and install packages into it
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

# Copy app code
COPY api.py /app/

# Create s6 service directory for our app
RUN mkdir -p /etc/services.d/jobwatcher

# Copy service run script into s6 location
COPY run.sh /etc/services.d/jobwatcher/run
RUN chmod +x /etc/services.d/jobwatcher/run
