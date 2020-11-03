import os
import sys
import pandas as pd
from loguru import logger

from workflow.scripts.utils import settings
from workflow.scripts.utils.general import (
    get_meta_data,
    get_schema_data,
    make_outDir,
    backup_processed_data,
    create_df,
)

env_configs = settings.env_configs


def type_compare(property, t1, t2):
    type_lists = [
        ["object", "string", "string[]"],
        ["int64", "integer"],
        ["float64", "float"],
    ]
    type_match = False
    for t in type_lists:
        if t1 in t and t2 in t:
            type_match = True
    if type_match == True:
        logger.info('Property "{}" types match - local:{} schema:{}', property, t1, t2)
    else:
        logger.warning(
            'Property "{}" types do not match - local:{} schema:{}', property, t1, t2
        )
    return type_match


def compare_df_to_schema(df_types, schema_info, node_rel):
    # logger.debug(schema_info)
    # logger.debug(df_types)
    schema_dic = {}
    keep_cols = []
    # get the schema name and data type info
    if not "properties" in schema_info:
        logger.error("Problem with the schema {}", df_types)
        exit()
    for i in schema_info["properties"]:
        schema_dic[i] = schema_info["properties"][i]["type"]

    # check required fields are there
    if "required" in schema_info:
        for i in schema_info["required"]:
            logger.info("{} is required", i)
            if i in df_types:
                logger.info("- match: {}", i)
            else:
                logger.error("{},'is missing from {}", i, df_types)
                exit()
    else:
        logger.error("There are no required properties, exiting")
        exit()

    # for all data, check they are in the schema
    for i in df_types:
        if i in schema_dic:
            keep_cols.append(i)
            type_compare(property=i, t1=df_types[i], t2=schema_dic[i])
        else:
            logger.error("ERROR - property {} not in schema {}", i, schema_dic)
            exit()

    return keep_cols


def dup_check(df, index_property):
    if not index_property in df:
        logger.error("index property '{}' missing from dataframe", index_property)
        exit()
    if df[index_property].duplicated().any():
        logger.error('Index column "{}" is not unique', index_property)
        dups = df[df[index_property].duplicated()]
        logger.error("\n{}", dups)
        logger.error("\n{}", df[index_property].value_counts())
        exit()


def df_check(df=[], meta_id=""):
    source_data = get_meta_data(meta_id=meta_id)
    meta_name = source_data["name"]
    meta_type = source_data["d_type"]
    schema_data = get_schema_data(meta_name=meta_name)
    # check index column is unique
    if "index" in schema_data:
        index_property = schema_data["index"]
        dup_check(df, index_property)

    outDir = make_outDir(meta_id)
    df_types = df.dtypes.apply(lambda x: x.name).to_dict()
    header = compare_df_to_schema(df_types, schema_data, meta_type)
    return header
