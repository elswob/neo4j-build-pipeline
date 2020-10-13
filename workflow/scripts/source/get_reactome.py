import pandas as pd
import os
import datetime

from workflow.scripts.utils import settings

env_configs = settings.env_configs

data_dir = os.path.join(env_configs["data_dir"], "reactome")
os.makedirs(data_dir,exist_ok=True)

today = datetime.date.today()


def protein_to_pathway():
    # protein to pathway
    url = "https://reactome.org/download/current/UniProt2Reactome_All_Levels.txt"
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
    print(df.head())
    df.to_csv(
        os.path.join(data_dir, f"UniProt2Reactome_All_Levels_human_{today}.csv"),
        index=False,
    )


def pathways():
    # pathways
    # complete list
    url = "https://reactome.org/download/current/ReactomePathways.txt"
    df1 = pd.read_csv(url, sep="\t")
    df1.columns = ["reactome_id", "name", "species"]
    df1 = df1[df1["species"] == "Homo sapiens"]
    print(df1.head())
    df1.to_csv(
        os.path.join(data_dir, f"ReactomePathways_human_{today}.csv"), index=False
    )

    # hierarchy
    url = "https://reactome.org/download/current/ReactomePathwaysRelation.txt"
    df2 = pd.read_csv(url, sep="\t")
    df2.columns = [
        "parent",
        "child",
    ]
    print(df2.head())
    print(df2.shape)
    df2 = df2[df2["parent"].isin(df1["reactome_id"])]
    print(df2.shape)
    df2.to_csv(
        os.path.join(data_dir, f"ReactomePathwaysRelation_human_{today}.csv"),
        index=False,
    )


if __name__ == "__main__":
    protein_to_pathway()
    pathways()
