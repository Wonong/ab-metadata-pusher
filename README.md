# ab-metadata-pusher
containerized metadata pusher using [Amundsendatabuilder](https://github.com/amundsen-io/amundsendatabuilder)

## How to run
(currently only mysql extractor and AWS SQS publisher work)
commands below runs sample job on `job/sample_mysql_aws_sqs_job.py`.
recommend using `.env` file rather than command line env.
```
docker build -t ab-metadata-pusher -f pusher-crontab.Dockerfile .
docker run ab-metadata-pusher \
        -e TARGET_DB_TYPE=mysql \
        -e TARGET_MESSAGE_QUEUE_TYPE=aws \
        -e JOB_SCHEDULE="your-cronjob-format-schedule" \
        -e AWS_SQS_REGION=your-region \
        -e AWS_SQS_URL=your-aws-sqs-url \
        -e AWS_SQS_ACCESS_KEY_ID=aws-access-key \
        -e AWS_SQS_SECRET_ACCESS_KEY=your-aws-secret-key \
        -e DATABASE_HOST=your-database-host-address \
        -e DATABASE_PORT=your-database-port \
        -e DATABASE_DB_NAME=your-database-db-name \
        -e DATABASE_USER=your-database-user-name \
        -e DATABASE_PASSWORD=your-database-password
```

## Concept

![components](docs/assets/metadata-pusher.png)
Amundsendatabuilder is a **Pull patten** Metadata builder. So, it runs mostly on server-side cluster(like airflow) and saves DB credentials to access databases. Also, To access database, There should be no firewall issues between the database and server-side cluster.
But, there are places where this method cannot be used due to problems such as firewalls and policies.
`ab-metadata-pusher` is **push pattern** databuilder which can be used in client-side cluster.
It just run ETL Task on client-side and publish result of task to message queue.
It follow ETL concept of amundsendatabuilder and use those components as it used in amundsendatabuilder.

## will be updated
- CI by github action: lint, mypy, ... 
- data sources: postgres,bigquery
- publish destination: kafka
- example cronjob file
- replace all sh script to python code


