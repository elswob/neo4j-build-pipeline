# neo4j-build-pipeline

![](https://github.com/elswob/neo4j-build-pipeline/workflows/Conda/badge.svg)

Neo4j data integration and build pipeline 

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

