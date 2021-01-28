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


def process():
    # select the file
    FILE = get_source(meta_id, 1)
    logger.info("Reading {}", FILE)
    df = pd.read_csv(os.path.join(dataDir, FILE))
    # logger.info(df.columns)
    logger.info(df.shape)

    # drop some columns
    df.drop(
        ["access", "priority", "coverage", ""], axis=1, inplace=True, errors="ignore"
    )
    logger.info(df.shape)

    # create the csv and import data
    create_import(df=df, meta_id=meta_id)

    # create constraints
    constraintCommands = [
        "CREATE CONSTRAINT ON (g:Gwas) ASSERT g.id IS UNIQUE",
        "CREATE index on :Gwas(trait)",
        "CREATE index on :Gwas(filename)",
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    process()
