# neo4j-build-pipeline

Neo4j data integration and build pipeline 

### Create .env file

Copy `.env.example` to `.env` and edit

```
cp .env.example .env
```

If not using remote server, leave the server environment variable empty 

### Create source data

Even if source data is pulled directly from an API, it needs to be stored somewhere, perferably with a version or date name.

Code to create source data should live in the `workflow/scripts/source` directory

Example:

```
python -m workflow.scripts.source.get_opengwas
```

###  Build data

- Run single step

```
todo
```

- Run all data build steps

```
snakemake -r check_new_data -j 10
```

### Build graph

Create neo4j directories

```
export $(cat .env | sed 's/#.*//g' | xargs)
mkdir -p $NEO4J_IMPORT_DIR $NEO4J_DATA_DIR $NEO4J_LOG_DIR
chmod 777 $NEO4J_IMPORT_DIR $NEO4J_DATA_DIR $NEO4J_LOG_DIR
```