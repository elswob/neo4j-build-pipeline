import os
import re
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

# args = the argparse arguments (-n name and -d data)
# dataDir = the path to the working directory for this node/rel
# dataFiles = dictionary of source files specified in data_integration.yml

#######################################################################


def process():
    FILE = os.path.basename(dataFiles['tophits'])
    df = pd.read_csv(os.path.join(dataDir, FILE), low_memory=False)
    df = df[["rsid"]].drop_duplicates()
    # change column name to match schema
    df.rename(columns={"rsid": "name"}, inplace=True)
    df['id']=df['name']

    create_import(df=df, meta_id=meta_id)

    # create constraints
    constraintCommands = [
        "CREATE CONSTRAINT ON (v:Variant) ASSERT v.name IS UNIQUE;",
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    process()
