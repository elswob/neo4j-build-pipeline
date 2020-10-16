# neo4j-build-pipeline

Neo4j data integration and build pipeline 


### Clone the repo and create conda environment

```
git clone git@github.com:elswob/neo4j-build-pipeline.git
```

If no conda, install miniconda3
- https://docs.conda.io/en/latest/miniconda.html

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh
```

Create conda environment

```
conda env create -f environment.yml
conda activate neo4j_build
```

### Create .env file

Copy `.env.example` to `.env` and edit

```
cp .env.example .env
```

- If not using remote server, leave the server environment variable empty 
- Modify the paths 

### Create source data

Even if source data is pulled directly from an API, it needs to be stored somewhere, perferably with a version or date name.

Code to create source data should live in the `workflow/scripts/source` directory

Example:

```
python -m test.source.get_opengwas
```

### Edit the config file

All data are handled by the `config/data_integration.yaml` file. 

Modify this to load new data:

```
gwas-opengwas:
name: Gwas
files:
    meta: opengwas/opengwas-metadata-2020-10-13.csv
script: nodes.gwas.opengwas
source: OpenGWAS-2020-10-13
```

###  Build data

- Run single step

```
python -m test.scripts.processing.nodes.gwas.opengwas -n gwas-opengwas
```

Take a look at the profiling html page, e.g. `nodes/gwas-opengwas/gwas-opengwas.profile.html`

- Run all data build steps

```
snakemake -r check_new_data -j 10
```

### Build graph

Create neo4j directories

```
python -m workflow.scripts.graph_build.create_neo4j
```

```
snakemake -j 10
```