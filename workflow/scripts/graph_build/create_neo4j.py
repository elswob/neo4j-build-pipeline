import os
from workflow.scripts.utils import settings
from loguru import logger

env_configs = settings.env_configs

NEO4J_IMPORT_DIR = env_configs["neo4j_log_dir"]
NEO4J_DATA_DIR = env_configs["neo4j_data_dir"]
NEO4J_LOG_DIR = env_configs["neo4j_import_dir"]

NLIST = [NEO4J_IMPORT_DIR, NEO4J_DATA_DIR, NEO4J_LOG_DIR]

for n in NLIST:
    logger.debug(n)
    os.makedirs(n, exist_ok=True)
    try:
        os.system(f"chmod 777 {n}")
    except:
        logger.error(
            "Error changing permission on neo4j directories, perhaps you don't have permission?"
        )
        exit()
