"""
Retrive OpenTargets data from api. Independent of epigraphdb existing data.
"""
from pathlib import Path
from typing import Generator, List
from multiprocessing import Pool, cpu_count
from loguru import logger
import os
import datetime
import requests
import pandas as pd

from workflow.scripts.utils import settings

env_configs = settings.env_configs

data_dir = os.path.join(env_configs["data_dir"], "opentargets")
os.makedirs(data_dir, exist_ok=True)

today = datetime.date.today()

# Params
N_PER_CHUNK = 100
N_PROCS = min(8, max(cpu_count() - 1, 1))
OPENTARGETS_API_URL = "https://api.opentargets.io/v3"
OPENTARGETS_TARGETS_URL = "https://storage.googleapis.com/open-targets-data-releases/19.11/output/19.11_target_list.csv.gz"
DATA_DIR = Path("~/data/export").expanduser()
OPENTARGETS_DIR = DATA_DIR / "opentargets"
OUTPUT_FILE = OPENTARGETS_DIR / "opentargets.csv"


def get_ensembl_id() -> List[str]:
    logger.info("get_ensembl_id")
    file_path_gz = Path("/tmp/19.11_target_list.csv.gz")
    with requests.get(OPENTARGETS_TARGETS_URL, stream=True) as r:
        r.raise_for_status()
        with open(file_path_gz, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    df = pd.read_csv(
        file_path_gz,
        header=None,
        names=[
            "ensembl_id",
            "hgnc_approved_symbol",
            "uniprot_accessions",
            "number_of_associations",
        ],
    )
    res = list(df["ensembl_id"])
    return res


def ot_query_api(gene_id_list: List[str]) -> Generator:

    drug_fields = [
        "target.id",
        "target.gene_info.symbol",
        "target.target_class",
        "evidence.target2drug.action_type",
        "disease.efo_info.efo_id",
        "evidence.drug2clinic.clinical_trial_phase.numeric_index",
        "unique_association_fields.chembl_molecules",
        "drug",
    ]
    payload = {
        "target": gene_id_list,
        "datatype": ["known_drug"],
        "fields": drug_fields,
        "size": 10_000,
    }
    request_url = f"{OPENTARGETS_API_URL}/platform/public/evidence/filter"
    r = requests.post(request_url, json=payload)

    for e in r.json()["data"]:
        yield (
            e["target"]["id"],
            e["target"]["gene_info"]["symbol"],
            e["target"]["target_class"][0],
            e["evidence"]["target2drug"]["action_type"],
            e["drug"]["molecule_name"],
            e["drug"]["molecule_type"],
            e["evidence"]["drug2clinic"]["clinical_trial_phase"]["numeric_index"],
            e["disease"]["efo_info"]["efo_id"],
            # e["unique_association_fields"]['chembl_molecules'],
            e["drug"]["id"],
        )


def get_ot_data(gene_id_list: List[str]) -> pd.DataFrame:
    cols = [
        "target_id",
        "target_symbol",
        "target_class",
        "action_type",
        "molecule_name",
        "molecule_type",
        "phase",
        # "indication",
        "efo_id",
        "chembl_uri",
    ]
    df = pd.DataFrame(ot_query_api(gene_id_list), columns=cols).drop_duplicates(
        subset=[
            "target_symbol",
            "chembl_uri",
            # 'indication',
        ]
    )
    return df


def main(oFile) -> None:
    gene_id_list = get_ensembl_id()

    with Pool(N_PROCS) as pool:
        nested_list = [
            gene_id_list[i : (i + N_PER_CHUNK)]
            for i in range(0, len(gene_id_list), N_PER_CHUNK)
        ]
        map_res = pool.map(get_ot_data, nested_list)
        ot_df = pd.concat(map_res, ignore_index=True)

    OPENTARGETS_DIR.mkdir(parents=True, exist_ok=True)
    ot_df.to_csv(oFile, index=False)


if __name__ == "__main__":
    main(oFile=os.path.join(data_dir, f"open_targets_{today}.csv"))
