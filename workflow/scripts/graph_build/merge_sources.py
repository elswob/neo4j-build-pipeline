import os
import sys
import re
import pandas as pd
import numpy as np
import argparse
import multiprocessing as mp

from loguru import logger
from workflow.scripts.utils import settings
from workflow.scripts.utils.general import (
    get_meta_data,
    make_outDir,
    create_df,
    get_schema_data,
)
from workflow.scripts.utils.writers import write_import
from functools import reduce

env_configs = settings.env_configs

SNAKEMAKELOGS = env_configs["snakemake_logs"]
THREADS = int(env_configs["threads"])

logger.add(os.path.join(SNAKEMAKELOGS, "merge.log"), colorize=True)

parser = argparse.ArgumentParser(description="Merge node sources")
parser.add_argument("-d,--dname", dest="dname", default="all")
parser.add_argument("-n,--nrows", dest="nrows", default=None)

args = parser.parse_args()
logger.debug(args)

# create merged directory
merge_dir = os.path.join(env_configs["neo4j_import_dir"], "nodes", "merged")
os.makedirs(merge_dir, exist_ok=True)


def find_multiple(source_data, data_type):
    d = {}
    for n in source_data[data_type]:
        name = source_data[data_type][n]["name"]
        if name in d:
            d[name].append(n)
        else:
            d[name] = [n]
    logger.info(d)
    return d


def create_single_column_v1(x, y):
    if not x == "":
        return x
    elif not y == "":
        return y
    else:
        return None


def create_single_column_v2(row, cols):
    d = [row[c] for c in cols]
    try:
        v = next(s for s in d if s)
        return v
    except:
        return ""


def column_conflict_check(df):
    cols = list(df.columns)
    trim_cols = {}
    for c in cols:
        c_trim = re.sub("_\w$", "", c)
        if c_trim in trim_cols:
            trim_cols[c_trim].append(c)
        else:
            trim_cols[c_trim] = [c]
    # find duplicate column names
    for t in trim_cols:
        if len(trim_cols[t]) > 1:
            logger.warning("Duplicate columns from merge {} {}", t, trim_cols[t])

            # rename columns to avoid problems with duplicate columns names after merge
            col_names = []
            new_names = []
            counter = 0
            for c in df.columns:
                if c in trim_cols[t]:
                    new_name = f"{c}{counter}"
                    counter += 1
                    col_names.append(new_name)
                    new_names.append(new_name)
                else:
                    col_names.append(c)
            df.columns = col_names

            # split df into chunks and process in parallel
            logger.info("Running column merge with {} threads", THREADS)
            df_chunks = np.array_split(df, THREADS)
            new_d = []
            with mp.Pool(THREADS) as pool:
                new_d.extend(
                    pool.starmap(
                        run_create_single, [(df_c, new_names) for df_c in df_chunks]
                    )
                )
            flat_list = [item for sublist in new_d for item in sublist]
            df[t] = flat_list
            df.drop(new_names, axis=1, inplace=True)
    return df


def run_create_single(df, cols):
    # logger.info(df.head())
    t = df.apply(lambda x: create_single_column_v2(x, cols), axis=1)
    return list(t)


def column_zero_fix(df):
    # issue with merging adding .0 to integers (might not be necessary now reading in CSV as str)
    for i in df.columns:
        name, data_type = i.split(":")
        # find data from schema that has been specified to be numerical, also catch IDs
        # if data_type in ['long','integer','int'] or data_type.startswith('ID'):
        if data_type in ["long", "integer", "int"]:
            logger.info("Dealing with possible integer problems {}", i)
            df[i] = df[i].astype(str).str.split(".", expand=True)[0]
    return df


def merge_source(meta_ids=[]):
    logger.debug("multi source {}", meta_ids)
    data_frames = []
    index_col = ""
    for i in meta_ids:
        logger.info("Processing meta_id: {}", i)
        meta_data = get_meta_data(i)
        schema_data = get_schema_data(meta_data["name"])
        logger.debug(schema_data)
        out_dir = make_outDir(meta_id=i)
        if not args.nrows is None:
            args.nrows = int(args.nrows)
        df = create_df(data_dir=out_dir, name=i, nrows=args.nrows)
        # make index column a string to avoid merge issues, e.g. float and object
        index_col = f"{schema_data['index']}:ID({meta_data['name']}-ID)"
        # logger.debug('index_col {}',index_col)
        # don't need to fix int/float issues anymore as reading everything in as strings
        # df = column_zero_fix(df)
        logger.debug("\n{}", df.head())
        logger.debug("\n{}", df.dtypes)
        data_frames.append(df)

        # get the constraints (not sure how to deal with multiple constraint files, assume they are the same...?)
        source_file = os.path.join(out_dir, i + "-constraint.txt")
        target_file = os.path.join(merge_dir, meta_data["name"] + "-constraint.txt")
        if os.path.exists(source_file):
            create_sym_link(source=source_file, target=target_file)

    logger.debug("index column: {}", index_col)
    # merge the dataframes on index
    logger.info("Merging {}", meta_ids)
    df_merged = reduce(
        lambda left, right: pd.merge(left, right, on=[index_col], how="outer"),
        data_frames,
    ).fillna("")
    logger.debug("\n{}", df_merged.head())

    # find duplicate source columns and aggregate
    source_cols = df_merged.filter(regex="^_source.*", axis=1)
    logger.info("Aggregating source columns {}", source_cols.columns)
    # aggregate into neo4j array style (separated by ;)
    source_agg = source_cols.agg(lambda x: ";".join(y for y in x if y != ""), axis=1)
    logger.debug("\n{}", source_agg.value_counts())
    # drop the merge source columns
    drop_cols = list(df_merged.filter(regex="^_source.*"))
    logger.debug("dropping cols {}", drop_cols)
    df_merged.drop(drop_cols, inplace=True, axis=1)
    # df_merged = df_merged[df_merged.columns.drop(drop_cols)]
    df_merged["_source:string[]"] = source_agg

    # check for column conflicts, e.g. b_x and b_y
    logger.info("Running conflict check with {} threads", THREADS)
    df_merged = column_conflict_check(df_merged)

    logger.debug("\n{}", df_merged.head())

    # issue with merging adding .0 to integers
    df = column_zero_fix(df_merged)

    # convert entire df to strings as don't need integers for neo4j import
    df_merged = df_merged.applymap(str)

    # need to convert nan to empty string
    df_merged = df_merged.replace("nan", "")
    df_merged = df_merged.replace("None", "")
    # logger.debug("\n{}",df_merged)

    return df_merged


def create_sym_link(source, target):
    source = os.path.abspath(source)
    target = os.path.abspath(target)
    if os.path.exists(target):
        os.unlink(target)
    # logger.debug('source {}, target {}',source,target)
    os.symlink(source, target)


def single_source(meta_id=""):
    meta_data = get_meta_data(meta_id=meta_id)
    out_dir = make_outDir(meta_id=meta_id)
    csv_file = os.path.join(out_dir, meta_id + ".csv.gz")
    csv_header = os.path.join(out_dir, meta_id + ".header")

    # create symlinks for import statements
    source_file = os.path.join(out_dir, meta_id + "-import-nodes.txt")
    target_file = os.path.join(merge_dir, meta_data["name"] + "-import-nodes.txt")
    create_sym_link(source=source_file, target=target_file)

    # create symlinks for constraint statements
    source_file = os.path.join(out_dir, meta_id + "-constraint.txt")
    target_file = os.path.join(merge_dir, meta_data["name"] + "-constraint.txt")
    if os.path.exists(source_file):
        create_sym_link(source=source_file, target=target_file)


def write_new_merged_files(df_merged, node_type):
    logger.info(node_type)
    df_merged.to_csv(
        os.path.join(merge_dir, node_type + ".csv.gz"), index=False, header=False
    )
    # logger.info(df_merged)
    o = open(os.path.join(merge_dir, node_type + ".header"), "w")
    o.write(",".join(df_merged.columns))
    o.close()

    # write the import command
    import_dir = os.path.join("import", "nodes", "merged")
    write_import(
        id=node_type,
        dir=merge_dir,
        importCommands=[
            {
                "type": "nodes",
                "name": node_type,
                "file": os.path.join(import_dir, node_type + ".csv.gz"),
                "header": os.path.join(import_dir, node_type + ".header"),
            }
        ],
    )


def get_source_data(dname="all"):
    logger.info('Running merge with "{}" data types', dname)
    source_data = get_meta_data(meta_id="all")
    node_d = find_multiple(source_data, "nodes")

    if not dname == "all":
        node_d = {dname: node_d[dname]}
    logger.debug(node_d)
    for i in node_d:
        # check if already done
        f = os.path.join(merge_dir, i + ".csv.gz")
        logger.debug("Checking if already done {}", f)
        if os.path.exists(f):
            logger.info("Already processed {}", i)
        else:
            logger.info("Processing node: {} ...", i)
            if len(node_d[i]) > 1:
                df_merged = merge_source(node_d[i])
                write_new_merged_files(df_merged, i)
            else:
                single_source(node_d[i][0])
            logger.info("Processed node: {}", i)


if __name__ == "__main__":
    get_source_data(dname=args.dname)
