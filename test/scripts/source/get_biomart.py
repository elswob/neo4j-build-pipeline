import gzip
import os
import sys
import datetime
import biomart
from biomart import BiomartServer
from loguru import logger

from workflow.scripts.utils import settings
from workflow.scripts.utils.general import copy_source_data

env_configs = settings.env_configs

data_name = "biomart"

today = datetime.date.today()


def biomart_to_file(atts, filename, type):
    logger.info("attributes: {} filename: {}", atts, filename)

    # latest build
    # server = BiomartServer( "http://www.ensembl.org/biomart" )
    # build 37
    server = biomart.BiomartServer("http://grch37.ensembl.org/biomart")

    hge = server.datasets["hsapiens_gene_ensembl"]
    # print(hge.show_attributes())

    s = hge.search({"attributes": atts}, header=1)
    o = gzip.open(filename, "w")
    c = 0
    for l in s.iter_lines():
        if c > 0:
            chr = l.decode("utf-8").split("\t")[0]
            if chr in [
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "18",
                "19",
                "20",
                "21",
                "22",
                "X",
                "Y",
            ]:
                # print(l.decode('utf-8').split('\t')[0])
                # added binary b for python 3
                if type == "protein":
                    chr, gene, protein = l.decode("utf-8").split("\t")
                    if len(protein) > 1:
                        o.write(l + b"\n")
                else:
                    o.write(l + b"\n")
        c += 1
    # copy to data directory
    copy_source_data(data_name, filename)


def create_clean_protein(protein_data):
    filename = f"/tmp/protein-only-{today}.txt"
    o = open(filename, "w")
    pCheck = {}
    with gzip.open(protein_data) as f:
        for line in f:
            chr, gene, uni = line.decode("utf-8").split("\t")
            if uni not in pCheck:
                o.write(uni)
                pCheck[uni] = ""
    o.close()
    copy_source_data(data_name, filename)


def get_biomart_data():
    logger.info("Getting biomart data from www.ensembl.org/biomart")
    gf1 = f"/tmp/gene-data-{today}.txt.gz"
    gf2 = f"/tmp/protein-data-sp-{today}.txt.gz"
    atts1 = [
        "chromosome_name",
        "gene_biotype",
        "external_gene_name",
        "description",
        "external_gene_source",
        "ensembl_gene_id",
        "start_position",
        "end_position",
    ]
    atts2 = ["chromosome_name", "ensembl_gene_id", "uniprotswissprot"]
    if os.path.exists(gf1):
        logger.info("biomart data already created", gf1)
    else:
        # atts = ['chromosome_name','gene_biotype','external_gene_name','description','external_gene_source','ensembl_gene_id','uniprotswissprot','entrezgene_id','start_position','end_position']
        # get all but swissprot
        biomart_to_file(atts1, gf1, "gene")
        # get ensembl gene and swissprot separately
        biomart_to_file(atts2, gf2, "protein")
        create_clean_protein(gf2)
    return atts1, atts2


if __name__ == "__main__":
    atts1, atts2 = get_biomart_data()
