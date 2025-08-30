FROM ghcr.io/home-assistant/amd64-base:latest


# Install Python + build deps + sqlite CLI
RUN apk add --no-cache python3 py3-pip build-base sqlite


WORKDIR /app

# Create venv and install packages into it
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

# Copy app code
COPY api.py /app/

RUN mkdir -p /data
# Copy seed DB
COPY jobs.db /app/
COPY jobs.db /data/

RUN mkdir -p /etc/cont-init.d
COPY 10-debug.sh /etc/cont-init.d/10-debug
RUN chmod +x /etc/cont-init.d/10-debug

# Create s6 service directory for our app
RUN mkdir -p /etc/services.d/jobwatcher

# Copy service run script into s6 location
COPY run.sh /etc/services.d/jobwatcher/run
RUN chmod +x /etc/services.d/jobwatcher/run




#RUN apk add --no-cache dos2unix \
 #&& dos2unix /etc/services.d/jobwatcher/run \
 #&& chmod +x /etc/services.d/jobwatcher/run \
 #&& ls -l /etc/services.d/jobwatcher \
 #&& head -1 /etc/services.d/jobwatcher/run


#RUN echo "== run.sh head ==" && head -5 /etc/services.d/jobwatcher/run
#RUN echo "== run.sh perms ==" && ls -l /etc/services.d/jobwatcher/

#RUN echo '#!/bin/sh\nexit 0' > /etc/services.d/jobwatcher/finish && chmod +x /etc/services.d/jobwatcher/finish
