import textwrap
import logging
import logging.config
import os
from pyhocon import ConfigFactory

from databuilder.extractor.postgres_metadata_extractor import PostgresMetadataExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.job.job import DefaultJob
from databuilder.task.task import DefaultTask

from publisher import aws_sqs_csv_puiblisher
from publisher.aws_sqs_csv_puiblisher import AWSSQSCsvPublisher

logging_config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config/logging_config.ini')
logging.config.fileConfig(logging_config_file_path)
LOGGER = logging.getLogger()

# TODO: AWS SQS url, region and credentials need to change
AWS_SQS_REGION = os.getenv('AWS_SQS_REGION', 'ap-northeast-2')
AWS_SQS_URL = os.getenv('AWS_SQS_URL', 'https://sqs.ap-northeast-2.amazonaws.com')
AWS_SQS_ACCESS_KEY_ID = os.getenv('AWS_SQS_ACCESS_KEY_ID', '')
AWS_SQS_SECRET_ACCESS_KEY = os.getenv('AWS_SQS_SECRET_ACCESS_KEY', '')

# TODO: connection string needs to change
# Source DB configuration
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
DATABASE_USER = os.getenv('DATABASE_USER', 'psql')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'psql')
DATABASE_DB_NAME = os.getenv('DATABASE_DB_NAME', 'postgres')
DATABASE_SCHEMA = os.getenv('DATABASE_SCHEMA', 'public')

POSTGRES_CONN_STRING = \
    f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB_NAME}'


def run_mysql_job() -> DefaultJob:
    where_clause_suffix = textwrap.dedent(f"""
        where c.table_schema = '{DATABASE_SCHEMA}'
    """)

    tmp_folder = '/var/tmp/amundsen/table_metadata'
    node_files_folder = '{tmp_folder}/nodes/'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships/'.format(tmp_folder=tmp_folder)

    job_config = ConfigFactory.from_dict({
        'extractor.postgres_metadata.{}'.format(PostgresMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY):
            where_clause_suffix,
        'extractor.postgres_metadata.{}'.format(PostgresMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME):
            True,
        'extractor.postgres_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING):
            POSTGRES_CONN_STRING,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH):
            node_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH):
            relationship_files_folder,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.NODE_FILES_DIR):
            node_files_folder,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.RELATION_FILES_DIR):
            relationship_files_folder,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.AWS_SQS_REGION):
            AWS_SQS_REGION,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.AWS_SQS_URL):
            AWS_SQS_URL,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.AWS_SQS_ACCESS_KEY_ID):
            AWS_SQS_ACCESS_KEY_ID,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.AWS_SQS_SECRET_ACCESS_KEY):
            AWS_SQS_SECRET_ACCESS_KEY,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.JOB_PUBLISH_TAG):
            'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=DefaultTask(extractor=PostgresMetadataExtractor(), loader=FsNeo4jCSVLoader()),
                     publisher=AWSSQSCsvPublisher())
    return job


if __name__ == "__main__":

    mysql_job = run_mysql_job()
    mysql_job.launch()
