import os
import sys
import pandas as pd
from loguru import logger

#################### leave me heare please :) ########################

from utils.general import setup

from utils.writers import (
    create_constraints,
    create_import,
)

# setup and return path to attribute directory
args, dataDir = setup()
meta_id = args.name

#######################################################################


def process():
    data = "opengwas-metadata.csv"
    df = pd.read_csv(os.path.join(dataDir, data))
    # logger.info(df.columns)
    logger.info(df.shape)

    # drop some columns
    df.drop(["access", "priority"], axis=1, inplace=True, errors="ignore")
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
