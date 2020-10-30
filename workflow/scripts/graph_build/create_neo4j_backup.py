import os
from workflow.scripts.utils import settings
from loguru import logger

env_configs = settings.env_configs

GRAPH_CONTAINER_NAME = env_configs['container_name']

try:
    os.system(f'docker exec --interactive --tty $GRAPH_CONTAINER_NAME bin/neo4j-admin backup --backup-dir data/dumps/')
except:
    logger.error("Error")
    exit()

