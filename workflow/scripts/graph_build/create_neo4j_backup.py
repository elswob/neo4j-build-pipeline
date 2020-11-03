import os
import subprocess
from workflow.scripts.utils import settings
from loguru import logger

env_configs = settings.env_configs

GRAPH_CONTAINER_NAME = env_configs["container_name"]
NEO4J_DATA_DIR = env_configs["neo4j_data_dir"]
SERVER = env_configs["server_name"]

try:
    # run neo4j-admin backup
    os.system(
        f"docker exec --interactive --tty $GRAPH_CONTAINER_NAME bin/neo4j-admin backup --backup-dir data/dumps/"
    )
    # copy to storage
    backup_dir = os.path.join(
        env_configs["graph_dir"], env_configs["graph_version"], "neo4j_backups"
    )
    logger.info("backup directory = {}", backup_dir)
    if SERVER == None:
        com = f"mkdir -p {backup_dir}"
    else:
        com = f"ssh {SERVER} mkdir -p {backup_dir}"
    logger.info(com)
    subprocess.call(com, shell=True)

    backup = f"$NEO4J_DATA_DIR/dumps/neo4j"
    logger.info("Syncing {}", backup)
    if SERVER == None:
        com = f"rsync -avz {backup} {backup_dir}"
    else:
        com = f"rsync -avz {backup} {SERVER}:{backup_dir}"
    logger.info(com)
    subprocess.call(com, shell=True)
except:
    logger.error("Error with backup")
    exit()
