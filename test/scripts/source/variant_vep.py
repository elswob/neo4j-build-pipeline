import subprocess
import pandas as pd
import os
import datetime

from workflow.scripts.utils import settings
from loguru import logger

env_configs = settings.env_configs

data_dir = os.path.join(env_configs["data_dir"], "vep")
os.makedirs(data_dir, exist_ok=True)

today = datetime.date.today()

# setup
# vep docker image needs setting up - note volumes need to be same for setup and run
# docker run -t -i -v /data/vep_data:/opt/vep/.vep ensemblorg/ensembl-vep perl INSTALL.pl -a cf -s homo_sapiens -y GRCh37

vep_data_dir = "/data/vep_data"


def process_variants(variant_file):
    df = pd.read_csv(variant_file, low_memory=False)
    df = df["rsid"]
    df.drop_duplicates(inplace=True)
    logger.info(df.head())
    # in this example, only run 100 variants as can be quite slow
    df.head(n=100).to_csv(
        f"{vep_data_dir}/variants-{today}.txt", index=False, header=False
    )


def run_vep(variant_dir, variant_file):
    com = """
        docker run -t -i -v {vep_data_dir}:/opt/vep/.vep 
        ensemblorg/ensembl-vep ./vep --port 3337 --cache --fork 20 --assembly GRCh37 
        -i /opt/vep/.vep/{variant_file} 
        -o /opt/vep/.vep/vep-{today}.txt 
        --per_gene 
        --no_intergenic
    """.format(
        vep_data_dir=vep_data_dir, variant_file=variant_file, today=today
    )
    com = com.replace("\n", " ")
    logger.info(com)
    subprocess.call(com, shell=True)
    # copy results
    com = f"cp /data/vep_data/vep-{today}.txt {env_configs['data_dir']}/vep/"
    subprocess.call(com, shell=True)


if __name__ == "__main__":
    process_variants(
        os.path.join(
            env_configs["data_dir"], "opengwas", "opengwas-tophits-2020-10-13.csv"
        )
    )
    run_vep("/tmp", f"variants-{today}.txt")
