import os
import requests
import json
import sys
import pandas as pd
import datetime

from loguru import logger
from workflow.scripts.utils import settings
from workflow.scripts.utils.general import copy_source_data

env_configs = settings.env_configs
data_name = "opengwas"

today = datetime.date.today()

gwas_data_file = f"/tmp/opengwas-metadata-{today}.csv"
gwas_tophits = f"/tmp/opengwas-tophits-{today}.csv"

def get_gwas_data():
    # create the data
    gwas_api_url = "http://gwasapi.mrcieu.ac.uk/gwasinfo"
    logger.info("Getting gwas data from {}", gwas_api_url)
    gwas_res = requests.get(gwas_api_url).json()
    outData = open(gwas_data_file, "w")
    df = pd.DataFrame(gwas_res)
    df = df.T.fillna("")
    logger.info(df.head())
    logger.info(df["year"].describe())
    df.to_csv(outData, index=False)
    outData.close()
    copy_source_data(data_name=data_name,filename=gwas_data_file)


def get_top_hits():
    df = pd.read_csv(gwas_data_file,low_memory=False)
    gwas_ids = list(df.id)
    logger.info(gwas_ids[0:10])
    gwas_api_url = "http://gwasapi.mrcieu.ac.uk/tophits"
    payload = {"id": gwas_ids, "preclumped": 1}
    response = requests.post(gwas_api_url, json=payload)
    res = response.json()
    th_df = pd.json_normalize(res)
    th_df.to_csv(gwas_tophits, index=False)
    copy_source_data(data_name=data_name,filename=gwas_tophits)


if __name__ == "__main__":
    get_gwas_data()
    get_top_hits()
