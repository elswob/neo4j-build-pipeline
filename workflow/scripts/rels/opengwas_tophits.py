import os
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


def gwas():
    data = "opengwas-tophits.csv"
    df = pd.read_csv(os.path.join(dataDir, data), low_memory=False)
    df = df[["id", "rsid", "beta", "p"]].drop_duplicates()

    # edit column names to match schema
    df.rename(columns={"id": "source", "rsid": "target", "p": "pval"}, inplace=True)

    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    gwas()
