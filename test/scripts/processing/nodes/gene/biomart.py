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


def gene():
    FILE = get_source(meta_id, 1)
    data = os.path.join(dataDir, FILE)
    df = pd.read_csv(data, sep="\t")
    # add column names
    col_names = [
        "chr",
        "type",
        "name",
        "description",
        "biomart_source",
        "ensembl_id",
        "start",
        "end",
    ]
    df.columns = col_names
    df.drop_duplicates(inplace=True)
    create_import(df=df, meta_id=meta_id)

    # create constraints
    constraintCommands = [
        "CREATE CONSTRAINT ON (g:Gene) ASSERT g.ensembl_id IS UNIQUE",
        "CREATE INDEX ON :Gene(name)",
        "CREATE INDEX ON :Gene(chr)",
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    gene()
