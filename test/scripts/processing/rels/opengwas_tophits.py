import os
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

FILE = get_source(meta_id,1)

def gwas():
    df = pd.read_csv(os.path.join(dataDir, FILE), low_memory=False)
    df = df[["id", "rsid", "beta", "p"]].drop_duplicates()

    # edit column names to match schema
    df.rename(columns={"id": "source", "rsid": "target", "p": "pval"}, inplace=True)

    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    gwas()
