import os
import gzip
import json
import sys
import pandas as pd
from loguru import logger

#################### leave me heare please :) ########################

from workflow.scripts.utils.general import setup

from workflow.scripts.utils.writers import (
    create_constraints,
    create_import,
)

# setup
args, dataDir, dataFiles = setup()
meta_id = args.name

# args = the argparse arguments (name and data)
# dataDir = the path to the working directory for this node/rel
# dataFiles = dictionary of source files specified in data_integration.yml

#######################################################################

FILE = os.path.basename(dataFiles["pathway"])

def process():
    df = pd.read_csv(os.path.join(dataDir, FILE))
    logger.info(df.head())
    keep_cols = ["parent", "child"]
    df = df[keep_cols]
    df.rename(columns={"parent": "target", "child": "source"}, inplace=True)
    df.drop_duplicates(inplace=True)
    logger.info(df.head())

    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    process()
