#!/command/with-contenv sh
set -x
echo ">>> JobWatcher run script starting..."
echo "PWD=$(pwd)"
ls -l /app
ls -l /data || echo "/data not found"

# Try touching the DB to confirm permissions
echo ">>> Checking DB path..."
ls -l /data/jobs.db || echo "DB not found"

# Now start uvicorn
exec /app/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8001