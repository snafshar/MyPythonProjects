# Python Practice Utilities

Small standard-library projects focused on readable code, validation, and tests.

## Modules
- `csv_summary.py`: summarize numeric columns in a CSV file.
- `json_validate.py`: validate JSON input and report useful errors.
- `text_stats.py`: count words, lines, and character frequencies.
- `retry.py`: reusable bounded retry helper.
- `tests/`: unit tests using `unittest`.

## Run tests
From this directory:

```bash
python3 -m unittest discover -s tests -v
```

All examples use the Python standard library. Avoid feeding untrusted, very large files to scripts without adding appropriate size and resource limits.
