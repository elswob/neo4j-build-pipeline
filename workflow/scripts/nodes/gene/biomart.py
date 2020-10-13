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

# args = the argparse arguments (name and data)
# dataDir = the path to the working directory for this node/rel
# dataFiles = dictionary of source files specified in data_integration.yml

#######################################################################


def gene():
    FILE = os.path.basename(dataFiles["gene"])
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
