#!/usr/bin/with-contenv sh
# s6 runs this as the main service for the add-on

# ensure config dir exists
mkdir -p /config/jobwatcher

# run the API
exec /app/run.sh
