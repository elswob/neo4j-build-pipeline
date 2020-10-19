# neo4j-build-pipeline

[![](https://github.com/elswob/neo4j-build-pipeline/workflows/Conda/badge.svg)](https://github.com/elswob/neo4j-build-pipeline/actions?query=workflow%3AConda)

Neo4j data integration and build pipeline 

This pipeline originated from the work done to create the graph for [EpiGraphDB](https://epigraphdb.org/). With over 20 separate data sets, >10 node types and >40 relationship types we needed to create a pipeline that could make the process relatively easy for others in the group to contribute. By combining [Snakemake](https://snakemake.readthedocs.io/), [Docker](https://www.docker.com/), [Neo4j](https://neo4j.com/) and [GitHub Actions](https://github.com/features/actions) we have created a pipeline that can create a fully tested Neo4j graph database from raw data. 

Components of interest:
- Pipeline can be used to prepare raw data, create files for graph, or build graph. 
- A definded schema is used to check all data before loading.
- Merging multiple data sets into a single node type is handled automatically.

## Setup

#### Clone the repo and create conda environment

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

#### Run build tests

```
snakemake -r clean_all -j 1
snakemake -r check_new_data -j 10
```

## Adding new data

[ADDING_DATA](ADDING_DATA.md)

## Build graph

#### 1. Create .env file

Copy `.env.example` to `.env` and edit

```
cp .env.example .env
```

- If not using remote server, leave the server environment variable empty 
- Modify the paths 

#### 2. Setup Neo4j directories before creating the graph (important!!!!)

Due to issues with Neo4j 4.* and Docker, need to manually create Neo4j directories before building the graph. If this is not done, Docker will create the Neo4j directories and make them unreadable.

```
python -m workflow.scripts.graph_build.create_neo4j
```

Note:
- Assumes docker is installed and runnning.

#### 3. Build the graph

```
snakemake -j 10
```

## Issues

Old version of docker-compose, just pip install a new one :)

```
pip install --user docker-compose
```

