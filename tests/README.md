# Unit tests

To trigger unit tests, at root of the repo, do
```
python -m pytest -vv
```

## Advance uses

Parallelised testing with multiple workers (8 workers `-n 8`)
```
python -m pytest -vv -n 8
```

Rerun testing with only tests that failed last time (`--lf`)
```
python -m pytest -vv --lf
```

Only do tests under a folder (e.g. "tests/schema")
```
python -m pytest -vv "tests/schema"
```
