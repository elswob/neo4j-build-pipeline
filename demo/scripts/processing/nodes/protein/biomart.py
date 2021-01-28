import os
import re
import gzip
import json
import sys
import pandas as pd

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


def protein():
    FILE = get_source(meta_id, 1)
    data = os.path.join(dataDir, FILE)
    df = pd.read_csv(data, sep="\t")
    df.columns = ["uniprot_id"]
    df["name"] = df["uniprot_id"]
    create_import(df=df, meta_id=meta_id)

    constraintCommands = [
        "CREATE CONSTRAINT ON (p:Protein) ASSERT p.uniprot_id IS UNIQUE",
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    protein()
