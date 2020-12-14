import sys
import textwrap
import uuid
from pyhocon import ConfigFactory

from databuilder.extractor.mysql_metadata_extractor import MysqlMetadataExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.extractor.neo4j_extractor import Neo4jExtractor
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.job.job import DefaultJob
from databuilder.task.task import DefaultTask


from publisher import aws_sqs_csv_puiblisher
from publisher.aws_sqs_csv_puiblisher import AWSSQSCsvPublisher

# TODO: AWS SQS url and credentials need to change
aws_sqs_url = 'aws_sqs_url'
aws_sqs_access_key_id = 'aws_sqs_access_key_id'
aws_sqs_secret_access_key = 'aws_sqs_secret_access_key'


# TODO: connection string needs to change
def connection_string():
    user = 'username'
    host = 'localhost'
    port = '3306'
    db = 'mysql'
    return "mysql://%s@%s:%s/%s" % (user, host, port, db)

def run_mysql_job():
    where_clause_suffix = textwrap.dedent("""
        where c.table_schema = 'mysql'
    """)

    tmp_folder = '/var/tmp/amundsen/table_metadata'
    node_files_folder = '{tmp_folder}/nodes/'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships/'.format(tmp_folder=tmp_folder)

    job_config = ConfigFactory.from_dict({
        'extractor.mysql_metadata.{}'.format(MysqlMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY):
            where_clause_suffix,
        'extractor.mysql_metadata.{}'.format(MysqlMetadataExtractor.USE_CATALOG_AS_CLUSTER_NAME):
            True,
        'extractor.mysql_metadata.extractor.sqlalchemy.{}'.format(SQLAlchemyExtractor.CONN_STRING):
            connection_string(),
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH):
            node_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH):
            relationship_files_folder,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.NODE_FILES_DIR):
            node_files_folder,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.RELATION_FILES_DIR):
            relationship_files_folder,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.AWS_SQS_URL):
            aws_sqs_url,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.AWS_SQS_ACCESS_KEY_ID):
            aws_sqs_access_key_id,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.AWS_SQS_SECRET_ACCESS_KEY):
            aws_sqs_secret_access_key,
        'publisher.awssqs.{}'.format(aws_sqs_csv_puiblisher.JOB_PUBLISH_TAG):
            'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=DefaultTask(extractor=MysqlMetadataExtractor(), loader=FsNeo4jCSVLoader()),
                     publisher=AWSSQSCsvPublisher())
    return job

if __name__ == "__main__":
    # Uncomment next line to get INFO level logging
    # logging.basicConfig(level=logging.INFO)

    mysql_job = run_mysql_job()
    mysql_job.launch()
