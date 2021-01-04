"""
This file is a modified version of amundsendatabuilder's example bigquery job source code.
This is a example script for extracting BigQuery usage results
"""
import logging
import logging.config
import os

from pyhocon import ConfigFactory

from databuilder.extractor.bigquery_metadata_extractor import BigQueryMetadataExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.task.task import DefaultTask
from databuilder.transformer.base_transformer import NoopTransformer

from publisher import aws_sqs_csv_puiblisher
from publisher.aws_sqs_csv_puiblisher import AWSSQSCsvPublisher

logging_config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config/logging_config.ini')
logging.config.fileConfig(logging_config_file_path)
LOGGER = logging.getLogger()

AWS_SQS_REGION = os.getenv('AWS_SQS_REGION', 'ap-northeast-2')
AWS_SQS_URL = os.getenv('AWS_SQS_URL', 'https://sqs.ap-northeast-2.amazonaws.com')
AWS_SQS_ACCESS_KEY_ID = os.getenv('AWS_SQS_ACCESS_KEY_ID', '')
AWS_SQS_SECRET_ACCESS_KEY = os.getenv('AWS_SQS_SECRET_ACCESS_KEY', '')

# Source Bigquery configuration
PROJECT_ID_KEY = os.getenv('PROJECT_ID_KEY', 'gcp-project-id')
CRED_KEY = os.getenv('CRED_KEY', 'gcp-cred-key')


# todo: Add a second model
def create_bq_job() -> DefaultJob:
    tmp_folder = f'/var/tmp/amundsen/bigquery-metadata'
    node_files_folder = f'{tmp_folder}/nodes'
    relationship_files_folder = f'{tmp_folder}/relationships'

    bq_meta_extractor = BigQueryMetadataExtractor()
    csv_loader = FsNeo4jCSVLoader()

    task = DefaultTask(extractor=bq_meta_extractor,
                       loader=csv_loader,
                       transformer=NoopTransformer())

    job_config = ConfigFactory.from_dict({
        f'extractor.bigquery_table_metadata.{BigQueryMetadataExtractor.PROJECT_ID_KEY}': PROJECT_ID_KEY,
        f'extractor.bigquery_table_metadata.{BigQueryMetadataExtractor.CRED_KEY}': CRED_KEY,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR}': True,
        f'publisher.awssqs.{aws_sqs_csv_puiblisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.awssqs.{aws_sqs_csv_puiblisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.awssqs.{aws_sqs_csv_puiblisher.AWS_SQS_REGION}': AWS_SQS_REGION,
        f'publisher.awssqs.{aws_sqs_csv_puiblisher.AWS_SQS_URL}': AWS_SQS_URL,
        f'publisher.awssqs.{aws_sqs_csv_puiblisher.AWS_SQS_ACCESS_KEY_ID}': AWS_SQS_ACCESS_KEY_ID,
        f'publisher.awssqs.{aws_sqs_csv_puiblisher.AWS_SQS_SECRET_ACCESS_KEY}': AWS_SQS_SECRET_ACCESS_KEY,
        f'publisher.awssqs.{aws_sqs_csv_puiblisher.JOB_PUBLISH_TAG}':
            'unique_tag'  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=AWSSQSCsvPublisher())
    return job


if __name__ == "__main__":
    # start table job
    job = create_bq_job()
    job.launch()