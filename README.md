# neo4j-build-pipeline

Neo4j data integration and build pipeline 

### Create .env file

Copy `.env.example` to `.env` and edit

```
cp .env.example .env
```

### Create source data

Even if source data is pulled directly from an API, it needs to be stored somewhere, perferably with a version or date name.

If not using remote server, leave the server environment variable empty 

Code to create source data should live in the `workflow/scripts/source` directory

