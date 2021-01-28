import subprocess
import pandas as pd
import os
import datetime

from loguru import logger
from workflow.scripts.utils import settings
from workflow.scripts.utils.general import copy_source_data

env_configs = settings.env_configs

data_name = "vep"

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
    filename = f"{vep_data_dir}/variants-{today}.txt"
    df.head(n=100).to_csv(
        filename, index=False, header=False
    )
    copy_source_data(data_name=data_name,filename=filename)

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
    #com = f"cp /data/vep_data/vep-{today}.txt {env_configs['data_dir']}/vep/"
    #subprocess.call(com, shell=True)
    copy_source_data(data_name=data_name,filename=f'{vep_data_dir}/vep-{today}.txt')


if __name__ == "__main__":
    process_variants(
        os.path.join(
            env_configs["data_dir"], "opengwas", "opengwas-tophits-2020-10-13.csv"
        )
    )
    run_vep(vep_data_dir, f"variants-{today}.txt")
