#!/usr/bin/with-contenv sh
exec /app/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8001
