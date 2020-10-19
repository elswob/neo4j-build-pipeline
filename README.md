# neo4j-build-pipeline

[![Tests](https://github.com/elswob/neo4j-build-pipeline/workflows/Conda/badge.svg)](https://github.com/elswob/neo4j-build-pipeline/actions?query=workflow%3ATests)

Neo4j data integration and build pipeline 

This pipeline originated from the work done to create the graph for [EpiGraphDB](https://epigraphdb.org/). With over 20 separate data sets, >10 node types and >40 relationship types we needed to create a pipeline that could make the process relatively easy for others in the group to contribute. By combining [Snakemake](https://snakemake.readthedocs.io/), [Docker](https://www.docker.com/), [Neo4j](https://neo4j.com/) and [GitHub Actions](https://github.com/features/actions) we have created a pipeline that can create a fully tested Neo4j graph database from raw data. 

Components of interest:
- Pipeline can be used to prepare raw data, create files for graph, or build graph. 
- A definded schema is used to check all data before loading.
- Merging multiple data sets into a single node type is handled automatically.

Note:
- This is not a fully tested pipeline, there are known issues with Docker and Neo4j that need careful consideration. 


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

## Saving and restoring database

- https://neo4j.com/docs/operations-manual/current/docker/maintenance/#docker-neo4j-backup

Get the env variables

```
export $(cat .env | sed 's/#.*//g' | xargs)
```

Create dump

```
#create dump 
docker exec --interactive --tty $GRAPH_CONTAINER_NAME bin/neo4j-admin backup --backup-dir data/dumps/
```

Copy to new location

```
scp -r $NEO4J_DATA_DIR/dumps/neo4j xxx:
```

On public server, create `data` directory

```
mkdir data
chmod 777 data
```

Move dump into data

```
mv neo4j ./data
```

Start container

```
docker-compose -f docker-compose-public.yml up -d
```

Stop neo4j but keep container open
```
public_container=db-public
docker exec -it $public_container cypher-shell -a neo4j://localhost:1234 -d system "stop database neo4j;"
```

Restore the backup
```
docker exec -it $public_container bin/neo4j-admin restore --from data/neo4j --verbose --force
```

Restart the database
```
docker exec -it $public_container cypher-shell -a neo4j://localhost:1234 -d system "start database neo4j;"
```
