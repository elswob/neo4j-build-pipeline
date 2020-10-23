# neo4j-build-pipeline

[![Tests](https://github.com/elswob/neo4j-build-pipeline/workflows/Tests/badge.svg)](https://github.com/elswob/neo4j-build-pipeline/actions?query=workflow%3ATests)

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


## Setup

- follows method from here - https://github.com/manubot/rootstock/blob/master/SETUP.md#configuration

#### Create a new GitGHub repo

Create an empty GitHub repository at [https://github.com/new](https://github.com/new). 

Make a note of user and repo name

```
OWNER=xxx
REPO=abc
```

#### Clone the repo and reconfigure

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

If no conda, install miniconda3
- https://docs.conda.io/en/latest/miniconda.html

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh
```

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

Copy `example.env` to `.env` and edit

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
