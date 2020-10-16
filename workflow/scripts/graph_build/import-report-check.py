import sys
import re
import pandas as pd
import os
from workflow.scripts.utils import settings
from loguru import logger

env_configs = settings.env_configs

SNAKEMAKE_LOGS = env_configs["snakemake_logs"]

logger.add(os.path.join(SNAKEMAKE_LOGS, "import_report.log"), colorize=True)


def check_logs():
    import_logs = sys.argv[1]

    logger.info("Reading {}", import_logs)

    with open(import_logs) as f:
        relDic = {"Other": 0}
        for line in f:
            x = re.search("(\(.*\)).*(\[.*\]).*(\(.*\))", line)
            if x:
                relID = x[1] + "-" + x[2] + "-" + x[3]
                if relID in relDic:
                    relDic[relID] += 1
                else:
                    relDic[relID] = 1
            else:
                relDic["Other"] += 1

    rel_df = pd.DataFrame([relDic]).T
    rel_df.columns = ["skipped rows"]
    rel_df.sort_values(by=["skipped rows"], inplace=True, ascending=False)
    logger.info("Skipped relationships\n {}", rel_df)


if __name__ == "__main__":
    check_logs()
