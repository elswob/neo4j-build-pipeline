import os
import ast
import sys
import subprocess
from workflow.scripts.utils.general import (
    make_outDir,
    get_meta_data,
    backup_processed_data,
    get_schema_data,
)
from workflow.scripts.utils import settings
from pandas_profiling import ProfileReport
from workflow.scripts.utils.qc import df_check
from loguru import logger

env_configs = settings.env_configs

THREADS = env_configs["threads"]

graph_user = env_configs["graph_user"]
graph_bolt_port = env_configs["graph_bolt"]
graph_password = env_configs["graph_pass"]


def node_meta_check(schema_data):
    if "meta" in schema_data:
        if "_name" in schema_data["meta"] and "_id" in schema_data["meta"]:
            return schema_data["meta"]
        else:
            logger.error("schema_data is missing _name or _id {}", schema_data["meta"])
            exit()
    else:
        logger.error("schema_data is meta data {}", schema_data)
        exit()


def write_to_load_script(dataName, dir, f, textList):
    o = open(os.path.join(dir, f), "w")
    o.write("echo Adding " + dataName + "...\n")
    for t in textList:
        o.write(
            "cypher-shell -a bolt://localhost:"
            + graph_bolt_port
            + " -u "
            + graph_user
            + " -p "
            + graph_password
            + " '"
            + t.rstrip()
            + "'"
            + "\n"
        )
    o.close()


def write_import(id, dir, importCommands):
    #need to check if import statement already exists
    #f = os.path.join(dir, headerData["fileName"])
    #if files doesn't exist, create it and close
    #if not os.path.exists(f):
    #    open(f, "a").close()
    #with open(f, "r+") as file:
    #    i = headerData["data"]
    #    for line in file:
    #        print(line)
    #        if line.startswith(i):
    #            logger.info("{} already in import statement", i)
    #        else:
    #            file.write(i + "\n")
    #exit()
    logger.info("id: {}, dir: {}, importCommans: {}", id, dir, importCommands)
    for i in importCommands:
        if i["type"] == "nodes":
            f = os.path.join(dir, id + "-import-nodes.txt")
            if not os.path.exists(f):
               open(f, "a").close()
            with open(f, "r+") as file:
                import_statement = "--nodes=" + i["name"] + '="' + i["header"] + "," + i["file"]
                for line in file:
                    if line.startswith(import_statement):
                        logger.info("{} already in import statement", import_statement)
                        break
                else:
                    file.write(f'{import_statement}"\n')
        elif i["type"] == "rels":
            f = os.path.join(dir, id + "-import-rels.txt")
            if not os.path.exists(f):
               open(f, "a").close()
            with open(f, "r+") as file:
                import_statement = "--relationships="+ i["name"]+ '="'+ i["header"]+ ","+ i["file"]
                for line in file:
                    if line.startswith(import_statement):
                        logger.info("{} already in import statement", import_statement)
                        break
                else:
                    file.write(f'{import_statement}"\n')

def write_header(dir, headerData):
    #need to check if import statement already exists
    f = os.path.join(dir, headerData["fileName"])
    o = open(f, "w")
    o.write(headerData["data"] + "\n")
    o.close()


def write_constraint(id, dir, constraintCommands):
    #need to check if constraint already exists
    f = os.path.join(dir, id + "-constraint.txt")
    #if files doesn't exist, create it and close
    if not os.path.exists(f):
        open(f, "a").close()
    for i in constraintCommands:
        with open(f, "r+") as file:
            for line in file:
                if line.startswith(i):
                    logger.info("{} already in constraint", i)
                    break
            else:
                if i.endswith(";"):
                    file.write(i + "\n")
                else:
                    file.write(i + ";" + "\n")


def pandas_profiler(df, meta_id):
    print("Profiling...", meta_id)
    df.reset_index(drop=True, inplace=True)
    outDir = make_outDir(meta_id)
    profile = ProfileReport(df, minimal=True, pool_size=10)
    profile.to_file(os.path.join(outDir, meta_id + ".profile.html"))


def create_import_commands(header, meta_id, import_type):
    outDir = make_outDir(meta_id)
    metaData = get_meta_data(meta_id)
    source_data = get_meta_data(meta_id=meta_id)
    meta_name = source_data["name"]
    meta_type = source_data["d_type"]
    schema_data = get_schema_data(meta_name=meta_name)
    # logger.debug(schema_data)

    if meta_type == "nodes":
        # convert node ID property to neo4j style
        if "index" in schema_data:
            index_property = schema_data["index"]
            li = header.index(index_property)
            logger.info("Index = {} {}", index_property, li)
            header[li] = index_property + ":ID(" + meta_name + "-ID)"
            logger.info(header)
        else:
            logger.error("Schema has no index, exiting")
            exit()
        # add meta _name and _id
        node_meta = node_meta_check(schema_data)
        # header.extend(['_name','_id'])

    elif meta_type == "rels":
        # convert relationships source/target properties to neo4j START END style
        source_index = header.index("source")
        source_id = schema_data["properties"]["source"]["type"]
        target_index = header.index("target")
        target_id = schema_data["properties"]["target"]["type"]
        header[source_index] = ":START_ID(" + source_id + "-ID)"
        header[target_index] = ":END_ID(" + target_id + "-ID)"

    # add property types
    for i, item in enumerate(header):
        if item in schema_data["properties"]:
            property_type = schema_data["properties"][item]["type"]
            # deal with arrays
            if property_type == "array":
                property_type = "string[]"
            elif property_type == "integer":
                property_type = "int"
            header[i] = item + ":" + property_type

    write_header(
        dir=outDir,
        headerData={"fileName": meta_id + ".header", "data": ",".join(header),},
    )
    # don't create import statements for load csv data
    if not import_type == "load":
        write_import(
            id=meta_id,
            dir=outDir,
            importCommands=[
                {
                    "type": metaData["d_type"],
                    "name": metaData["name"],
                    "file": os.path.join(
                        "import", metaData["d_type"], meta_id, meta_id + ".csv.gz"
                    ),
                    "header": os.path.join(
                        "import", metaData["d_type"], meta_id, meta_id + ".header"
                    ),
                }
            ],
        )


def create_constraints(coms=[], meta_id=""):
    outDir = make_outDir(meta_id)
    # constraints
    write_constraint(id=meta_id, dir=outDir, constraintCommands=coms)


def create_import(df=[], meta_id="", import_type="import"):
    # qc the df
    schema_cols = df_check(df, meta_id)
    logger.info("Matched these columns {}", schema_cols)

    # add source column to node headers and df if node
    # meta_data = get_meta_data(meta_id)
    # if meta_data["d_type"] == "nodes":
    #    schema_cols.append("source:string[]")
    #    df["source:string[]"] = meta_data["source"]

    # add source info to nodes and rels
    meta_data = get_meta_data(meta_id)
    schema_cols.append("_source:string[]")
    df["_source:string[]"] = meta_data["source"]

    # add meta cols _name and _id to nodes
    if meta_data["d_type"] == "nodes":
        source_data = get_meta_data(meta_id=meta_id)
        meta_name = source_data["name"]
        schema_data = get_schema_data(meta_name=meta_name)
        logger.debug(schema_data)

        node_meta = node_meta_check(schema_data)
        # get type for _name and _id col
        name_col_type = schema_data["properties"][node_meta["_name"]]["type"]
        name_col_text = f"_name:{name_col_type}"
        id_col_type = schema_data["properties"][node_meta["_id"]]["type"]
        id_col_text = f"_id:{id_col_type}"

        # add to schema cols
        schema_cols.extend([name_col_text, id_col_text])

        # add to dataframe
        df[name_col_text] = df[node_meta["_name"]]
        df[id_col_text] = df[node_meta["_id"]]
        logger.debug("\n{}", df.head())

        # add indexes for meta properties
        constraintCommands = [
            f"CREATE index on :{meta_name}(_name);",
            f"CREATE index on :{meta_name}(_id);",
        ]
        create_constraints(constraintCommands, meta_id)

    # create copy of header for import creation
    logger.info("Creating import statement")
    import_header = schema_cols.copy()
    create_import_commands(
        header=import_header, meta_id=meta_id, import_type=import_type
    )

    outDir = make_outDir(meta_id)
    # logger.debug(outDir)
    file_name = os.path.join(outDir, meta_id + ".csv.gz")
    df.to_csv(
        file_name, index=False, header=False, compression="gzip", columns=schema_cols
    )

    # run pandas profiling
    com = f"sh workflow/scripts/utils/pandas-profiling.sh {outDir} {meta_id} {THREADS}"
    logger.debug(com)
    try:
        out = subprocess.check_output(com, shell=True)
        logger.info(out)
    except:
        logger.error(
            "Pandas profiling didn't work, perhaps you haven't installed shuf, see README.md?"
        )
        exit()

    # backup
    backup_processed_data(outDir, meta_id, meta_data["d_type"])
