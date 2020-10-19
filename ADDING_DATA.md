## Example

#### Opentargets DRUG-TARGET data

1. Create new branch

```
```

2. Create .env file

Copy `.env.example` to `.env` and edit

```
cp .env.example .env
```

- If not using remote server, leave the server environment variable empty 
- Modify the paths 

3. If necessary, create the source data

```
python -m test.scripts.source.get_opentargets
```

4. Edit `data_integration.yml`

- Node
```
  drug-ot:
    name: Drug
    raw:
      - opentargets/ot.csv
    script: nodes.drug.opentargets
    source: Opentargets-2020-10-19
```

- Relationship
```
  ot-drug-target:
    name: OPENTARGETS_DRUG_TO_TARGET
    raw:
      - opentargets/ot.csv
    script: rels.opentargets_drug_target
    source: Opentargets-2020-08-24
```

5. Edit `db_schema.yml`

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

6. Write a load script for both node and relationship

- Node
  ```

  ```

7. Test the build for new data only

8. Look at the profiling output

9. Test the entire build

10. Commit code to new branch and check Github actions  

https://github.com/elswob/neo4j-build-pipeline/actions

11. Go and lie down :)