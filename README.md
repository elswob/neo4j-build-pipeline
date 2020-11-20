# neo4j-build-pipeline

[![Tests](https://github.com/elswob/neo4j-build-pipeline/workflows/Tests/badge.svg)](https://github.com/elswob/neo4j-build-pipeline/actions?query=workflow%3ATests)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4243027.svg)](https://doi.org/10.5281/zenodo.4243027)

Neo4j data integration and build pipeline - https://github.com/elswob/neo4j-build-pipeline

This pipeline originated from the work done to create the graph for [EpiGraphDB](https://epigraphdb.org/). With over 20 separate data sets, >10 node types and >40 relationship types we needed to create a pipeline that could make the process relatively easy for others in the group to contribute. By combining [Snakemake](https://snakemake.readthedocs.io/), [Docker](https://www.docker.com/), [Neo4j](https://neo4j.com/) and [GitHub Actions](https://github.com/features/actions) we have created a pipeline that can create a fully tested Neo4j graph database from raw data. 

One of the main aims of this pipeline was performance. Initial efforts used the `LOAD CSV` method, but quickly became slow as the size and complexity of the graph increased. Here we focus on creating clean data sets that can be loaded using the `neo4j-import` tool, bringing build time down from hours to minutes. 

Components of interest:
- Pipeline can be used to prepare raw data, create files for graph, or build graph. 
- A defined schema is used to QC all data before loading.
- Merging multiple data sets into a single node type is handled automatically.
- Use `neo4j-import` to build the graph

Note:
- This is not a fully tested pipeline, there are known issues with Docker and Neo4j that need careful consideration. 

## Prerequisites

#### Conda (required)

Install miniconda3
- https://docs.conda.io/en/latest/miniconda.html

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh
```

#### Docker and Docker Compose (only required if building a graph)

Docker (17.06.0-ce) - https://docs.docker.com/get-docker/
Docker Compose (v1.27.4) - https://docs.docker.com/compose/install/

#### shuf (or gshuf)

For linux distributions this should be ok, but for mac, may need to install coreutils

```
brew install coreutils
```

## Basic setup

The following will run the test data and create a basic graph

```
#clone the repo (use https if necessary)
git clone git@github.com:elswob/neo4j-build-pipeline.git
cd neo4j-build-pipeline
#create the conda environment
conda env create -f environment.yml
conda activate neo4j_build
#create a basic environment variable file for test data - this probably requires some edits, but may work as is
cp example.env .env 
#run the pipeline
snakemake -r all -j 4
```

## Full setup

#### Clone the repo

If just testing, simply clone the repo `git clone git@github.com:elswob/neo4j-build-pipeline.git` and skip straight to [Create conda environment](#create-conda-environment)

If creating a new pipeline and graph based on this repo there are two options:

1. Fork the repo and skip straight to [Create conda environment](#create-conda-environment)
2. Create a copy of the repo, see below:

##### Create a new GitGHub repo

- follows method from here - https://github.com/manubot/rootstock/blob/master/SETUP.md#configuration

Create an empty GitHub repository at [https://github.com/new](https://github.com/new). 

Make a note of user and repo name

```
OWNER=xxx
REPO=abc
```

##### Clone the repo and reconfigure

```
git clone git@github.com:elswob/neo4j-build-pipeline.git
cd neo4j-build-pipeline
```

Set the origin URL to match repo created above

```
git remote set-url origin https://github.com/$OWNER/$REPO.git
git remote set-url origin git@github.com:$OWNER/$REPO.git
```

Push to new repo

```
git push --set-upstream origin main
```

#### Create conda environment

```
conda env create -f environment.yml
conda activate neo4j_build
```

#### Run build tests

```
snakemake -r clean_all -j 1
snakemake -r check_new_data -j 4
```

## Adding new data

[ADDING_DATA](ADDING_DATA.md)

## Build graph

A complete run of the pipeline will create a Neo4j graph within a Docker container, on the machine running the pipeline. The variables that are used for that are defined in the `.env` file.

#### 1. Create .env file

Copy `example.env` to `.env` and edit

```
cp example.env .env
```

- Modify this
- No spaces in paths please :)
- Use absolute/relative paths where stated
- If using remote server for raw data and backups, set SERVER_NAME and set up SSH keys [Remote Server](REMOTE_SERVER.md)

```
### Data integration variables

#version of graph being built
GRAPH_VERSION=0.0.1

#location of snakemake logs (relative or absolute)
SNAKEMAKE_LOGS=test/results/logs

#neo4j directories (absolute)
NEO4J_IMPORT_DIR=./test/neo4j/0.0.1/import
NEO4J_DATA_DIR=./test/neo4j/0.0.1/data
NEO4J_LOG_DIR=./test/neo4j/0.0.1/logs

#path to directory containing source data (absolute)
DATA_DIR=test/source_data
#path to directory containing data processing script directories and code (relative)
PROCESSING_DIR=test/scripts/processing
#path to directory for graph data backups (relative or absolute)
GRAPH_DIR=test/results/graph_data

#path to config (relative or absolute)
CONFIG_PATH=test/config

#name of server if source data is on a remote machine, not needed if all data are local
#SERVER_NAME=None

#number of threads to use for parallel parts
THREADS=10

############################################################################################################

#### Docker things for building graph, ignore if not using

# GRAPH_CONTAINER_NAME:
# Used in docker-compose and snakefile to
# assign container name to the db service to use docker exec
GRAPH_CONTAINER_NAME=neo4j-pipeline-demo-graph

#Neo4j server address (this will be the server running the pipeline and be used to populate the Neo4j web server conf)
NEO4J_ADDRESS=neo4j.server.com

# Neo4j connection
GRAPH_USER=neo4j
GRAPH_HOST=localhost
GRAPH_PASSWORD=changeme
GRAPH_HTTP_PORT=27474
GRAPH_BOLT_PORT=27687
GRAPH_HTTPS_PORT=27473

# Neo4j memory
# Set these to something suitable, for testing the small example data 1G should be fine. For anything bigger, see https://neo4j.com/developer/kb/how-to-estimate-initial-memory-configuration/
GRAPH_HEAP_INITIAL=1G
GRAPH_PAGECACHE=1G
GRAPH_HEAP_MAX=2G
```

#### 2. Build the graph

```
snakemake -r all -j 4
```

You should then be able to explore the graph via Neo4j browser by visiting the URL of the server hosting the graph plus the `GRAPH_HTTP_PORT` number specified, e.g. `localhost:27474`. Here you can login with the following

- Connect URL = `bolt://` `name_of_server`:`GRAPH_BOLT_PORT from .env`
- Authentication type = `Username/Password`
- Username = `GRAPH_USER from .env`
- Password = `GRAPH_PASSWORD from .env` 

## Issues

#### docker-compose version

Old version of docker-compose, just pip install a new one :)

```
pip install --user docker-compose
```

#### Neo4j directories need to be created before creating the Neo4j container 

Due to issues with Neo4j 4.* and Docker, need to manually create Neo4j directories before building the graph. If this is not done, Docker will create the Neo4j directories and make them unreadable.

- this happens during Snakemake `create_graph` rule via `workflow.scripts.graph_build.create_neo4j`.   
- to run this manually

```
python -m workflow.scripts.graph_build.create_neo4j
```

#### Port clashes

If this error:

```
Bind for 0.0.0.0:xxx failed: port is already allocated
```

Then need to change ports in `.env` as they are already being used by another container

```
GRAPH_HTTP_PORT=17474
GRAPH_BOLT_PORT=17687
GRAPH_HTTPS_PORT=17473
```

#### Docker group

When building the graph, if the user is not part of the docker group may see an error like this

```
Starting database...
Creating Neo4j graph directories
.....
PermissionError: [Errno 13] Permission denied
```

To fix this, need to be added to docker group

https://docs.docker.com/engine/install/linux-postinstall/

```
sudo usermod -aG docker $USER
```

## Saving and restoring database 

#### Creating a backup

- https://neo4j.com/docs/operations-manual/current/docker/maintenance/#docker-neo4j-backup

```
snakemake -r backup_graph -j1
```

#### Restoring a backup

On production server, create `data` directory

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

## Merging upstream changes

Again, based on logic from here - https://github.com/manubot/rootstock/blob/master/SETUP.md#merging-upstream-rootstock-changes

```
#checkout new branch
git checkout -b nbp-$(date '+%Y-%m-%d')
```

Pull new commits from neo4j-build-pipeline

```
#if remote not set
git config remote.neo4j-build-pipeline.url || git remote add neo4j-build-pipeline https://github.com/elswob/neo4j-build-pipeline.git

#pull new commits
git pull --no-ff --no-rebase --no-commit neo4j-build-pipeline main
```

If no problems, commit new updates

```
git commit -am 'merging upstream changes'
git push origin nbp-$(date '+%Y-%m-%d')
```

Then open a pull request

## Visualise

https://snakemake.readthedocs.io/en/v5.1.4/executable.html#visualization

```
snakemake -r all --dag | dot -Tpdf > dag.pdf
snakemake -r all --rulegraph | dot -Tpdf > rulegraph.pdf
```

## Report

https://snakemake.readthedocs.io/en/stable/snakefiles/reporting.html

```
Run this after the workflow has finished
snakemake --report report.html
```