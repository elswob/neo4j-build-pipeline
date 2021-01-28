import pandas as pd
import os
import datetime
from loguru import logger
from workflow.scripts.utils import settings
from workflow.scripts.utils.general import copy_source_data

env_configs = settings.env_configs

data_name = "reactome"

today = datetime.date.today()


def protein_to_pathway():
    # protein to pathway
    url = "https://reactome.org/download/current/UniProt2Reactome_All_Levels.txt"
    logger.info(url)
    df = pd.read_csv(url, sep="\t")
    df.columns = [
        "source_id",
        "reactome_id",
        "url",
        "event",
        "evidence_code",
        "species",
    ]
    df = df[df["species"] == "Homo sapiens"]
    logger.info(df.head())
    filename = f"/tmp/UniProt2Reactome_All_Levels_human_{today}.csv"
    df.to_csv(
        filename,
        index=False,
    )
    copy_source_data(data_name=data_name,filename=filename)


def pathways():
    # pathways
    # complete list
    url = "https://reactome.org/download/current/ReactomePathways.txt"
    logger.info(url)
    df1 = pd.read_csv(url, sep="\t")
    df1.columns = ["reactome_id", "name", "species"]
    df1 = df1[df1["species"] == "Homo sapiens"]
    logger.info(df1.head())
    filename = f"/tmp/ReactomePathways_human_{today}.csv"
    df1.to_csv(
        filename, index=False
    )
    copy_source_data(data_name=data_name,filename=filename)

    # hierarchy
    url = "https://reactome.org/download/current/ReactomePathwaysRelation.txt"
    logger.info(url)
    df2 = pd.read_csv(url, sep="\t")
    df2.columns = [
        "parent",
        "child",
    ]
    logger.info(df2.head())
    logger.info(df2.shape)
    df2 = df2[df2["parent"].isin(df1["reactome_id"])]
    logger.info(df2.shape)
    filename = f"/tmp/ReactomePathwaysRelation_human_{today}.csv"
    df2.to_csv(
        filename,
        index=False,
    )
    copy_source_data(data_name=data_name,filename=filename)

if __name__ == "__main__":
    protein_to_pathway()
    pathways()
