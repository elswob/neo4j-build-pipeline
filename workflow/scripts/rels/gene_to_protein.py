import os
import re
import gzip
import json
import sys
import pandas as pd

#################### leave me heare please :) ########################

from workflow.scripts.utils.general import setup

from workflow.scripts.utils.writers import (
    create_constraints,
    create_import,
)

# setup 
args, dataDir, dataFiles = setup()
meta_id = args.name

# args = the argparse arguements (name and data)
# dataDir = the path to the working directory for this node/rel
# dataFiles = dictionary of source files specified in data_integration.yml

#######################################################################


def gene_protein():
    FILE = os.path.basename(dataFiles['protein'])
    data = os.path.join(dataDir, FILE)
    df = pd.read_csv(data, sep="\t")
    df.columns = ["chr", "source", "target"]
    df.drop(columns=["chr"], inplace=True)
    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    gene_protein()
