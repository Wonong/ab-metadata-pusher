#!/bin/bash

get_assigned_job() {
    echo $((cat /app/config/docker.conf | pyhocon -f properties | grep database.$TARGET_DB_TYPE.job.$TARGET_MESSAGE_QUEUE_TYPE) | cut -d'=' -f2)
}

# configure job file path which will be executed by crontab
export JOB_PATH=$(get_assigned_job)

# export all environment variables to use in cron
env | sed 's/^\(.*\)$/export \1/g' >> /app/shell/envs.sh

# Update permission to execute.
chmod +x /app/shell/envs.sh
chmod +x /app/shell/run_job.sh

# Replace JOB_SCHEDULE to environment variable.
# TODO: Combine two statements below to a single statement
sed -i 's!$JOB_SCHEDULE!'"$JOB_SCHEDULE"'!g' /etc/cron.d/pusher-cron
sed -i 's!"!''!g' /etc/cron.d/pusher-cron

cron -f
