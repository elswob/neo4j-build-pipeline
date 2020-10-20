## Example

- Opentargets DRUG-TARGET data

#### 1. Create new branch

```
git checkout -b dev-$USER
```

#### 2. Create .env file

Copy `example.env` to `.env` and edit

```
cp .env.example .env
```

- Modify the paths 
- If not using remote server, leave the server environment variable empty 
- If using a remote server, need to set up SSH keys and SSH agent - see [REMOTE_SERVER.md](REMOTE SERVER)

#### 3. If necessary, create the source data

- this can be done on a remote server, just need to add `SERVER_NAME` name to `.env`

```
python -m test.scripts.source.get_opentargets
```

#### 4. Edit `data_integration.yml`

- Node
```
  drug-ot:
    name: Drug
    files:
      drug-target: opentargets/open_targets_2020-10-19.csv
    script: nodes.drug.opentargets
    source: Opentargets-2020-10-19
```

- Relationship
```
  ot-drug-target:
    name: OPENTARGETS_DRUG_TO_TARGET
    files:
      drug-target: opentargets/open_targets_2020-10-19.csv
    script: rels.opentargets_drug_target
    source: Opentargets-2020-08-24
```

#### 5. Edit `db_schema.yml`

- Node
```
  Drug:
    properties:
      id:
        type: string
      label:
        type: string
      molecule_type:
        type: string
    required:
      - label
      - id
    index: label
    meta:
      _id: id
      _name: label  
```

- Relationship
```
  OPENTARGETS_DRUG_TO_TARGET:
    properties:
      source:
        type: Drug
      target:
        type: Gene
      action_type:
        type: string
      phase:
        type: string
    required:
      - source
      - target 
      - phase
      - action_type
  ```

#### 6. Write a load script for both node and relationship

- if new node type make a new directory, e.g. `mkdir workflow/scripts/nodes/drug`

To access source files specified in `data_integraion.yml` use the key/value pairs, e.g.

```
FILE = get_source(meta_id,'drug-target')
```

To process the final dataframe

```
create_import(df=df, meta_id=meta_id)
```

To add constraints, e.g. Neo4j property indexes

```
constraintCommands = ["CREATE index on :Drug(label);"]
create_constraints(constraintCommands, meta_id)
```

#### 7. Test the build for new data only

```
python -m test.scripts.processing.nodes.drug.opentargets -n drug-ot
python -m test.scripts.processing.rels.opentargets_drug_target -n ot-drug-target
```

#### 8. Look at the profiling output

e.g. ./test/results/graph_data/0.0.1/nodes/gwas-opengwas/gwas-opengwas.profile.html

#### 9. Test the entire build

```
snakemake -r check_new_data -j 10
```

#### 10. Commit code to new branch and check the result of Github actions  

https://github.com/elswob/neo4j-build-pipeline/actions

