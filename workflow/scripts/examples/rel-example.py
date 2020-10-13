import os
import sys
import pandas as pd
from loguru import logger

#################### leave me heare please :) ########################

from utils.general import setup

from utils.writers import (
    create_constraints,
    create_import,
)

meta_id = sys.argv[1]

# setup and return path to attribute directory
dataDir = setup(meta_id=meta_id)

#######################################################################

FILE = "ieu-gwas-cosine-20200821.tsv.gz"


def process():
    #load predicate data
    logger.info('loading data...')
    df = pd.read_csv(os.path.join(dataDir, FILE),sep='\t',compression='gzip')
    logger.info(df.shape)
    col_names=['source','target','score']
    df.columns=col_names
    df.drop_duplicates(inplace=True)
    logger.info(df.shape)
    logger.info('\n {}',df)

    create_import(df=df, meta_id=meta_id)


if __name__ == "__main__":
    process()
    
