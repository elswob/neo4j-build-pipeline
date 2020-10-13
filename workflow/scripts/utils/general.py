"""
General-purpose helper functions
"""

import pathlib
from typing import List
from workflow.scripts.utils import settings
import yaml
import os
import git
import subprocess
import pandas as pd
import argparse
from loguru import logger

env_configs = settings.env_configs

graph_host = env_configs["graph_host"]
graph_user = env_configs["graph_user"]
graph_bolt_port = env_configs["graph_bolt"]
graph_password = env_configs["graph_pass"]


def neo4j_connect():
    from neo4j.v1 import GraphDatabase, basic_auth

    auth_token = basic_auth(graph_user, graph_password)
    driver = GraphDatabase.driver(
        "bolt://" + graph_host + ":" + graph_bolt_port, auth=auth_token, encrypted=False
    )
    return driver


def here(path: str = "") -> str:
    """Prepend path with the root directory path, similar to
    the approach in r-lib/here.
    """
    repo = git.Repo(pathlib.Path.cwd(), search_parent_directories=True)
    root = repo.git.rev_parse("--show-toplevel")
    here_path = pathlib.PurePath().joinpath(root, path)
    here = str(here_path)
    return here


def flatten_list(input: List, remove_null: bool = True) -> List:
    """Flatten a list:
    [[1, 2], [3, 4]] => [1, 2, 3, 4]
    :param input: a list
    :param remove_null: whether to remove None elements from
                        the flattened list
    :return: a flattened list
    """
    flattened_list = sum(input, [])
    if remove_null:
        flattened_list = [elem for elem in flattened_list if elem is not None]
    return flattened_list


def argparser():
    # todo
    parser = argparse.ArgumentParser(description="Node/relationship processing")

    parser.add_argument("-n,--name", dest="name")
    parser.add_argument("-d,--data", dest="data", default=False)

    args = parser.parse_args()
    logger.debug(args)

    if args.name == None:
        logger.error("Please provide a name, e.g. -n gwas-opengwas")
        exit()

    return args


def setup():
    args = argparser()
    meta_id = args.name
    IMPORTLOGS = env_configs["import_logs"]
    os.makedirs(IMPORTLOGS,exist_ok=True)
    # modify loguru log
    logger.add(os.path.join(IMPORTLOGS, meta_id + ".log"), colorize=True)
    meta_data = get_meta_data(meta_id)
    logger.info("meta_data {}", meta_data)
    outDir = make_outDir(meta_id)
    os.makedirs(outDir,exist_ok=True)
    try:
        os.remove(outDir + "/import*")
    except:
        logger.info("import clean")

    # get the raw data
    get_data(meta_data, meta_id, args)

    dataFiles = meta_data["files"]
    return args, outDir, dataFiles


def get_meta_data(meta_id):
    with open("config/data_integration.yaml") as file:
        source_data = yaml.load(file, Loader=yaml.FullLoader)
    if meta_id in source_data["nodes"]:
        m = source_data["nodes"][meta_id]
        m["d_type"] = "nodes"
    elif meta_id in source_data["rels"]:
        m = source_data["rels"][meta_id]
        m["d_type"] = "rels"
    else:
        m = source_data
    return m


def get_schema_data(meta_name="all"):
    with open("config/db_schema.yaml") as file:
        schema_data = yaml.load(file, Loader=yaml.FullLoader)
    if not meta_name == "all":
        if meta_name in schema_data["meta_nodes"]:
            schema_data = schema_data["meta_nodes"][meta_name]
        elif meta_name in schema_data["meta_rels"]:
            schema_data = schema_data["meta_rels"][meta_name]
    return schema_data


def get_data_from_server(dataName, outDir):
    logger.info("Getting data from server {}", dataName)
    dataDir = os.path.join(env_configs["data_dir"], dataName)
    server = env_configs["server_name"]
    com = f"rsync -avz {server}:{dataDir} {outDir}/"
    logger.info(com)
    subprocess.call(com, shell=True)
    # check the file copied ok
    fName = os.path.basename(dataName)
    if os.path.exists(os.path.join(outDir, fName)):
        logger.info("rsync of {}:{} to {} {} ok", server, dataName, outDir, fName)
    else:
        logger.error("rsync of {}:{} to {} {} failed", server, dataName, outDir, fName)
        exit()


def get_data_from_local(dataName, outDir, localDir):
    logger.info("Getting data from local {} {}", dataName, localDir)
    com = f"cp {localDir}/{dataName} {outDir}/"
    logger.info(com)
    try:
        subprocess.check_output(com, shell=True)
    except subprocess.CalledProcessError as e:
        logger.warning("Local copy failed")
        exit()


# fetch the data from server or local
def get_data(metaData, meta_id, args):
    server = env_configs["server_name"]
    logger.info("{} {} {} {}", metaData, meta_id, args.data, server)
    outDir = make_outDir(meta_id)
    for i in metaData["files"]:
        if args.data != False:
            get_data_from_local(metaData["files"][i], outDir, args.data)
        elif server != None:
            get_data_from_server(metaData["files"][i], outDir)
        else:
            localDir = env_configs["data_dir"]
            get_data_from_local(metaData["files"][i], outDir, localDir)


def backup_processed_data(p_file, meta_id, d_type):
    # make sure graph directory exists
    server = env_configs["server_name"]
    metadir = os.path.join(
        env_configs["graph_dir"], env_configs["graph_version"], d_type, meta_id
    )

    if server == None:
        com = f"mkdir -p {metadir}"
    else:
        com = f"ssh {server} mkdir -p {metadir}"
    subprocess.call(com, shell=True)

    logger.info("Syncing {}", p_file)
    if server == None:
        com = f"rsync -avz {p_file}/{meta_id}* {metadir}"
    else:
        com = f"rsync -avz {p_file}/{meta_id}* {server}:{metadir}"
    logger.info(com)
    subprocess.call(com, shell=True)


def make_outDir(meta_id):
    meta_data = get_meta_data(meta_id)
    try:
        outDir = os.path.join(env_configs["import_dir"], meta_data["d_type"], meta_id)
        return outDir
    except:
        logger.error(
            'Something wrong with meta_id "{}", perhaps it does not exists in data-integration.yaml',
            meta_id,
        )
        exit()


def process_header(header_file):
    include_cols = []
    header_cols = []
    rel_terms = ["START_ID", "END_ID"]
    for i in range(0, len(header_file)):
        if "IGNORE" in header_file[i]:
            col_name = header_file[i]
        elif any(r in header_file[i] for r in rel_terms):
            col_name = header_file[i]
        else:
            # col_name = header_file[i].split(':')[0]
            col_name = header_file[i]
            include_cols.append(col_name)
        header_cols.append(col_name)
    return include_cols, header_cols


# create a dataframe from any procssed data directory
def create_df(data_dir, name, nrows=None):
    csv_file = os.path.join(data_dir, name + ".csv.gz")
    header_file = (
        open(os.path.join(data_dir, name + ".header"), "r").read().rstrip().split(",")
    )
    include_cols, header_cols = process_header(header_file)
    # print(include_cols,header_cols)
    logger.debug(include_cols)
    logger.debug(header_cols)
    logger.debug("Creating df from {} {} ", csv_file, header_file)
    # read all data as str, to avoid issues with int/float formatting
    df = pd.read_csv(
        csv_file, names=header_cols, usecols=include_cols, dtype=str, nrows=nrows
    )
    return df
