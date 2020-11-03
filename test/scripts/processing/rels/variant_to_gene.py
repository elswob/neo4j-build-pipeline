import os
import re
import gzip
import sys
import csv
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

# args = the argparse arguements (name and data)
# dataDir = the path to the working directory for this node/rel

#######################################################################

vep_data = get_source(meta_id, 1)


def process_data():
    logger.info("Processing vep data {}", vep_data)
    col_names = [
        "source",
        "location",
        "allele",
        "target",
        "feature",
        "feature_type",
        "consequence",
        "cdna_position",
        "cds_position",
        "protein_position",
        "amino_acids",
        "codons",
        "existing_variation",
        "extra",
    ]

    # create csv file
    df = pd.read_csv(os.path.join(dataDir, vep_data), sep="\t", comment="#")
    df.drop_duplicates(inplace=True)
    df.columns = col_names
    print(df.head())
    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    process_data()
