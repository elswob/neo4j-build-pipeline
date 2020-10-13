import os
import re
import gzip
import json
import sys
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


def gene_protein():
    data = os.path.join(dataDir, "protein-data-sp.txt.gz")
    df = pd.read_csv(data, sep="\t")
    df.columns = ["chr", "source", "target"]
    df.drop(columns=["chr"], inplace=True)
    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    gene_protein()
