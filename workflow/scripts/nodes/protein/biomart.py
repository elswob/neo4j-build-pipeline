import os
import re
import gzip
import json
import sys
import pandas as pd

#################### leave me heare please :) ########################

from utils.general import setup, get_meta_data

from utils.writers import (
    create_constraints,
    create_import,
)


# setup and return path to attribute directory
args, dataDir = setup()
meta_id = args.name

#######################################################################


def protein():
    data = os.path.join(dataDir, "protein-only.txt")
    df = pd.read_csv(data, sep="\t")
    df.columns = ["uniprot_id"]
    df['name']=df['uniprot_id']
    create_import(df=df, meta_id=meta_id)

    constraintCommands = [
        "CREATE CONSTRAINT ON (p:Protein) ASSERT p.uniprot_id IS UNIQUE",
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    protein()
