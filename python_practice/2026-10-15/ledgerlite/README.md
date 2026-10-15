# LedgerLite

A dependency-free Python command-line expense tracker that stores entries as JSON.

## Requirements

Python 3.10 or newer.

## Examples

```bash
python ledgerlite.py add 12.50 lunch --category food
python ledgerlite.py add 4.20 bus --category transport
python ledgerlite.py list
python ledgerlite.py summary
python ledgerlite.py --file demo.json add 8.00 notebook --category study
```

The default data file is `ledgerlite.json` in the current directory. Use `--file` to select another file.

## Features

- Validate positive amounts and non-empty descriptions
- Record a category and UTC timestamp
- List recorded expenses
- Summarize spending by category and in total
- Write JSON through a temporary file before replacing the data file

This is a learning project, not accounting or tax software.
