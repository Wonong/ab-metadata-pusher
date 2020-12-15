#!/bin/bash

# export all environment variables to use in cron
env | sed 's/^\(.*\)$/export \1/g' >> /app/shell/envs.sh

# Update permission to execute.
chmod +x /app/shell/envs.sh
chmod +x /app/shell/run_job.sh

cron -f
