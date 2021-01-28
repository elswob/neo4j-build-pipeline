import os
import gzip
import json
import sys
import pandas as pd
from loguru import logger

#################### leave me heare please :) ########################

from workflow.scripts.utils.general import setup, get_source

from workflow.scripts.utils.writers import (
    create_constraints,
    create_import,
)

# setup
args, dataDir = setup()
meta_id = args.name

# args = the argparse arguments (name and data)
# dataDir = the path to the working directory for this node/rel

#######################################################################

FILE = get_source(meta_id, 1)


def process():
    df = pd.read_csv(os.path.join(dataDir, FILE))
    logger.info(df.head())
    keep_cols = ["source_id"]
    df = df[keep_cols]
    df.rename(columns={"source_id": "uniprot_id"}, inplace=True)
    df["name"] = df["uniprot_id"]
    df.drop_duplicates(inplace=True)
    logger.info(df.head())

    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    process()
