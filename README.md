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

### 