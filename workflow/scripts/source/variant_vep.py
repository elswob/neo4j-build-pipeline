import subprocess
import pandas as pd
import os
import gzip
from config import load_csv_dir, data_dir

outDir = "data"


def get_existing_data():
    subprocess.call(
        "rsync -avz "
        + os.path.join(data_dir, "xqtl-processed", "xqtl_single_snp.csv")
        + " "
        + outDir,
        shell=True,
    )
    subprocess.call(
        "rsync -avz "
        + os.path.join(data_dir, "mr-eve", "19_02_21", "variants.csv.gz")
        + " "
        + outDir,
        shell=True,
    )


def get_top_hits():
    df = pd.read_csv(gwas_data_file, sep="\t", header=None)
    gwas_ids = list(df[13])
    print(gwas_ids[0:10])
    # gwas_ids = gwas_ids[0:2]
    gwas_api_url = "http://gwasapi.mrcieu.ac.uk/tophits"
    payload = {"id": gwas_ids, "preclumped": 1}
    gwas_res = requests.post(gwas_api_url, json=payload)
    # print(gwas_res.json())
    oFile = os.path.join(outDir, "tophits.tsv")
    o = open(oFile, "w")
    for g in gwas_res.json():
        try:
            o.write(
                g["id"]
                + "\t"
                + g["rsid"]
                + "\t"
                + str(g["p"])
                + "\t"
                + str(g["beta"])
                + "\n"
            )
        except:
            print("Bad format\n", g)
    o.close()


def process_data():
    variant_data = set()
    # xqtl
    xqtl_data = "xqtl_single_snp.csv"
    print("Parsing...", xqtl_data)
    with open(os.path.join(outDir, xqtl_data)) as f:
        next(f)
        for line in f:
            exposure, outcome, b, se, p, qtl_type, rsid = line.rstrip().split(",")
            variant_data.add(rsid)

    # mr-eve
    mr_eve_data = "variants.csv.gz"
    with gzip.open(os.path.join(outDir, mr_eve_data), "r") as f:
        next(f)
        for line in f:
            l = line.decode("utf-8").rstrip().split(",")
            snp = l[5].replace('"', "")
            variant_data.add(snp)

            # IGD tophits
    igd_tophits_data = "tophits.tsv"
    with gzip.open(os.path.join(outDir, igd_tophits_data), "r") as f:
        next(f)
        for line in f:
            l = line.decode("utf-8").rstrip().split("\t")
            snp = l[1]
            variant_data.add(snp)

    # write to file
    s = open(os.path.join(outDir, "variants.tsv"), "w")
    for i in list(variant_data):
        s.write(i + "\n")
    s.close()


if __name__ == "__main__":
    get_existing_data()
    get_top_hits()
    process_data()
