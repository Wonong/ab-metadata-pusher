# ab-metadata-pusher
containerized metadata pusher using [Amundsendatabuilder](https://github.com/amundsen-io/amundsendatabuilder)

## Concept

![components](docs/assets/metadata-pusher.png)
Amundsendatabuilder is a **Pull patten** Metadata builder. So, it runs mostly on server-side cluster(like airflow) and keep DB credentials to access databases. Also, to access database, there should be no firewall issues between the database and server-side cluster.
But, there are places where this method cannot be used due to problems such as firewalls and policies.

`ab-metadata-pusher` is a **Push pattern** databuilder which can be run in client-side cluster.
It just run ETL Task on client-side and publish result of task to message queue.
It follow ETL concept of amundsendatabuilder and use those components as it used in amundsendatabuilder. But, its publisher has a different purpose, pushing extracted metadata to message queue.

## How to run
### Crontab docker
1. build docker image
2. run docker container with required environment variables

Commands below runs sample job of `job/sample_mysql_aws_sqs_job.py`. Recommendation is  using `.env` file rather than command line env since too many environment variables needed.

You can customize job configuration by updating `config/docker.conf`

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
### Required ENVs for each DB target
| TARGET_DB_TYPE | Required ENVs |
|----------------|---------------|
|mysql| DATABASE_HOST, DATABASE_PORT, DATABASE_DB_NAME, DATABASE_USER, DATABASE_PASSWORD|
|postgres| DATABASE_HOST, DATABASE_PORT, DATABASE_DB_NAME, DATABASE_SCHEMA, DATABASE_USER, DATABASE_PASSWORD|

### Required ENVs for each Message Queue target
| TARGET_MESSAGE_QUEUE_TYPE | Required ENVs |
|---------------------------|---------------|
| aws | AWS_SQS_REGION, AWS_SQS_URL, AWS_SQS_ACCESS_KEY_ID, AWS_SQS_SECRET_ACCESS_KEY |



## will be updated
- data sources: bigquery
- publish destination: kafka
- example cronjob file
- replace all sh script to python code
