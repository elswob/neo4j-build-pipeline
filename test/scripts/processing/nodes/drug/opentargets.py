import os
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
    data = os.path.join(dataDir, FILE)
    df = pd.read_csv(data, sep=",")
    logger.info("\n {}", df.head())
    keep_cols = ["molecule_name", "molecule_type", "chembl_uri"]
    df = df[keep_cols]
    col_names = ["label", "molecule_type", "id"]
    df.columns = col_names
    df.drop_duplicates(inplace=True)
    # set label to uppercase
    df["label"] = df["label"].str.upper()
    logger.info(df.shape)
    logger.info("\n {}", df.head())
    create_import(df=df, meta_id=meta_id)

    # create constraints
    constraintCommands = ["CREATE index on :Drug(label);"]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    process()
