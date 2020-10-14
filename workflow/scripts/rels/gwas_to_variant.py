import os
import re
import gzip
import json
import sys
import csv
import pandas as pd

#################### leave me heare please :) ########################

from utils.general import setup, get_source

from utils.writers import (
    create_constraints,
    create_import,
)


# setup and return path to attribute directory
args, dataDir = setup()
meta_id = args.name

#######################################################################


def process_data():
    print("Processing instruments...")
    csv_data = []
    col_names = [
        "target",
        "source",
        "beta",
        "se",
        "pval",
        "eaf",
        "samplesize",
        "ncase",
        "ncontrol",
    ]
    with gzip.open(os.path.join(dataDir, "instruments.csv.gz"), "rt") as f:
        next(f)
        filereader = csv.reader(f, delimiter=",")
        for line in filereader:
            variant, gwas, beta, se, pval, eaf, samplesize, ncase, ncontrol = line
            try:
                float(pval)
                float(se)
                float(eaf)
            except ValueError:
                continue
            if not gwas.startswith("UKB"):
                gwas = "IEU-a-" + gwas
            gwas = gwas.replace(":", "-")
            t = [
                variant,
                gwas.lower(),
                beta,
                se,
                pval,
                eaf,
                str(int(float(samplesize))),
                ncase,
                ncontrol,
            ]
            csv_data.append(t)

    # create csv file
    df = pd.DataFrame(csv_data)
    df.columns = col_names
    print(df.head())
    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    process_data()
