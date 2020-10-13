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

meta_id = sys.argv[1]

# setup and return path to attribute directory
dataDir = setup(meta_id=meta_id)

#######################################################################


def process():
    data = "opengwas-metadata.csv"
    df = pd.read_csv(os.path.join(dataDir, data))

    logger.info(df.shape)
    logger.info("\n{}", df.head())

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
