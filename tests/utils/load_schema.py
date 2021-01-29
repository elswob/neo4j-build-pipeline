from pathlib import Path

import yaml

from workflow.scripts.utils.settings import env_configs

config_path = Path(env_configs["config_path"])
schema_file = config_path / "db_schema.yaml"

with schema_file.open() as f:
    schema_dict = yaml.load(f, Loader=yaml.FullLoader)

meta_node_dict = schema_dict["meta_nodes"]
meta_rel_dict = schema_dict["meta_rels"]
meta_node_names = sorted(list(schema_dict["meta_nodes"].keys()))
meta_rel_names = sorted(list(schema_dict["meta_rels"].keys()))
