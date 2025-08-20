#!/usr/bin/env sh
set -e

# place persistent data in /config/jobwatcher
cd /app
# start the API
uvicorn api:app --host 0.0.0.0 --port 8001
