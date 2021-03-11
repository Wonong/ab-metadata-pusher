import os

from pyhocon import ConfigFactory
import fileinput

#  Initialize $JOB_PATH
conf = ConfigFactory.parse_file('/app/config/docker.conf')

container_type = os.getenv('TYPE')
target_db_type = os.getenv('TARGET_DB_TYPE')
target_message_queue_type = os.getenv('TARGET_MESSAGE_QUEUE_TYPE')

if container_type == 'pusher':
    os.setenv('JOB_PATH', conf[container_type]['database'][target_db_type]['job'][target_message_queue_type])
elif container_type == 'subscriber':
    os.setenv('JOB_PATH', conf[container_type]['message_queue'][target_message_queue_type]['job'][target_db_type])

# Replace $JOB_SCHEDULE in crontab file to env
job_schedule = os.getenv('JOB_SCHEDULE')

with fileinput.input(files='/etc/cron.d/cron', inplace=True) as f:
    for line in f:
        print(line.replace('$JOB_SCHEDULE', job_schedule), end='\n')


