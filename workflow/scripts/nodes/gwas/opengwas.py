import os
import sys
import pandas as pd
from loguru import logger

#################### leave me heare please :) ########################

from workflow.scripts.utils.general import setup

from workflow.scripts.utils.writers import (
    create_constraints,
    create_import,
)

# setup and return path to attribute directory
args, dataDir, dataFiles = setup()
meta_id = args.name

# args = the argparse arguements (name and data)
# dataDir = the path to the working directory for this node/rel
# dataFiles = the source files specified in data_integration.yml

#######################################################################


def process():
    FILE = os.path.basename(dataFiles[1])
    logger.info('Reading {}',FILE)
    df = pd.read_csv(os.path.join(dataDir, FILE))
    # logger.info(df.columns)
    logger.info(df.shape)

    # drop some columns
    df.drop(["access", "priority","coverage"], axis=1, inplace=True, errors="ignore")
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
