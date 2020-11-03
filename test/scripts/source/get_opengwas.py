import os
import requests
import json
import sys
import pandas as pd
import datetime

from workflow.scripts.utils import settings

env_configs = settings.env_configs

data_dir = os.path.join(env_configs["data_dir"], "opengwas")
os.makedirs(data_dir, exist_ok=True)

today = datetime.date.today()

gwas_data_file = os.path.join(data_dir, f"opengwas-metadata-{today}.csv")


def get_gwas_data():
    # create the data
    gwas_api_url = "http://gwasapi.mrcieu.ac.uk/gwasinfo"
    print("Getting gwas data from", gwas_api_url)
    gwas_res = requests.get(gwas_api_url).json()
    outData = open(gwas_data_file, "w")
    df = pd.DataFrame(gwas_res)
    df = df.T.fillna("")
    print(df.head())
    print(df["year"].describe())
    df.to_csv(outData, index=False)
    outData.close()


def get_top_hits():
    df = pd.read_csv(gwas_data_file)
    gwas_ids = list(df.id)
    print(gwas_ids[0:10])
    gwas_api_url = "http://gwasapi.mrcieu.ac.uk/tophits"
    payload = {"id": gwas_ids, "preclumped": 1}
    response = requests.post(gwas_api_url, json=payload)
    res = response.json()
    th_df = pd.json_normalize(res)
    th_df.to_csv(os.path.join(data_dir, f"opengwas-tophits-{today}.csv"), index=False)


if __name__ == "__main__":
    get_gwas_data()
    get_top_hits()
