import os
import sys

from workflow.scripts.utils import settings
from workflow.scripts.utils.general import get_meta_data

env_configs = settings.env_configs

graph_bolt_port = env_configs["graph_bolt"]
graph_user = env_configs["graph_user"]
graph_password = env_configs["graph_pass"]
neo4j_import_dir = env_configs["neo4j_import_dir"]

constraints = []
import_nodes = []
import_rels = []

source_data = get_meta_data(meta_id="all")

# loop through nodes merged directory
d = os.path.join(neo4j_import_dir, "nodes", "merged")
for filename in os.listdir(d):
    if filename.endswith("constraint.txt"):
        with open(os.path.join(d, filename)) as f:
            for line in f:
                if not line.startswith("#"):
                    constraints.append("echo '" + line.rstrip() + "'")
                    constraints.append(
                        "cypher-shell -a bolt://localhost:"
                        + graph_bolt_port
                        + " -u "
                        + graph_user
                        + " -p "
                        + graph_password
                        + " '"
                        + line.rstrip()
                        + "'"
                    )
    elif filename.endswith("import-nodes.txt"):
        with open(os.path.join(d, filename)) as f:
            for line in f:
                import_nodes.append(line.rstrip())

for i in source_data["rels"]:
    d = os.path.join(neo4j_import_dir, "rels", i)
    for filename in os.listdir(d):
        if filename.endswith("constraint.txt"):
            with open(os.path.join(d, filename)) as f:
                for line in f:
                    if not line.startswith("#"):
                        constraints.append("echo '" + line.rstrip() + "'")
                        constraints.append(
                            "cypher-shell -a bolt://localhost:"
                            + graph_bolt_port
                            + " -u "
                            + graph_user
                            + " -p "
                            + graph_password
                            + " '"
                            + line.rstrip()
                            + "'"
                        )
        if filename.endswith("import-rels.txt"):
            with open(os.path.join(d, filename)) as f:
                for line in f:
                    import_rels.append(line.rstrip())

o = open(os.path.join(neo4j_import_dir, "master_import.sh"), "w")

o.write("echo Importing data...\n")
o.write(
    """
neo4j-admin import \
--skip-bad-relationships \
--high-io=true \
--report-file=/var/lib/neo4j/logs/import.report \\
"""
)

for i in import_nodes:
    o.write(i + " \\\n")
if len(import_rels) > 0:
    for i in import_rels[0:-1]:
        o.write(i + " \\\n")
    o.write(import_rels[-1])
o.write("\n")

o.close()

o = open(os.path.join(neo4j_import_dir, "master_constraints.sh"), "w")
o.write("\necho Creating indexes and contraints...\n")
for c in constraints:
    o.write(c + "\n")
o.write("echo Done")
o.close()
