#!/command/with-contenv sh
cd /app
if [ ! -f /data/jobs.db ]; then
  echo ">>> Seeding jobs.db into /data"
  cp /etc/jobserver/seed.db /data/jobs.db
fi
echo ">>> JobWatcher starting..."
exec /app/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8001
