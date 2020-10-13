import os
import re
import gzip
import sys
import csv
import pandas as pd

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

vep_data = "variants-24-08-20.txt"


def process_data():
    print("Processing mr data...")
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
