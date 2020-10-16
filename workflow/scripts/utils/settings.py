from environs import Env

# Loads environmental variables from .env
env = Env()
env.read_env()

import_dir = env("NEO4J_IMPORT_DIR", "neo4j/import")
snakemake_logs = env("SNAKEMAKE_LOGS")
data_dir = env("DATA_DIR", "data_dir")
processing_dir = env("PROCESSING_DIR", "workflow/scripts/processing")
log_dir = env("NEO4J_LOG_DIR", "log_dir")
graph_dir = env("GRAPH_DIR")
server_name = env("SERVER_NAME", None)
graph_version = env("GRAPH_VERSION")
container_name = env("GRAPH_CONTAINER_NAME")
threads = env("THREADS", 4)

graph_bolt = env("GRAPH_BOLT_PORT")
graph_pass = env("GRAPH_PASSWORD")
graph_user = env("GRAPH_USER")
graph_host = env("GRAPH_HOST")

env_configs = {
    "import_dir": import_dir,
    "snakemake_logs": snakemake_logs,
    "data_dir": data_dir,
    "processing_dir": processing_dir,
    "log_dir": log_dir,
    "graph_dir": graph_dir,
    "server_name": server_name,
    "graph_version": graph_version,
    "graph_bolt": graph_bolt,
    "graph_pass": graph_pass,
    "graph_user": graph_user,
    "graph_host": graph_host,
    "container_name": container_name,
    "threads": threads,
}
