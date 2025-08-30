#!/command/with-contenv sh
echo ">>> cont-init.d debug: container starting up"
ls -l /
ls -l /app
ls -l /data || echo "/data not present at cont-init"
