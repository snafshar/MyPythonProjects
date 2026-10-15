# Python CLI Examples

Examples to run from this directory:

```bash
python3 path_report.py .
python3 ini_inspect.py sample.ini
python3 datetime_tools.py
python3 number_stats.py
python3 -m unittest discover -s tests -v
```

Some scripts are reusable modules rather than complete file-based applications. Import their functions from your own code or extend them with `argparse`. Add tests when changing behavior and keep external dependencies explicit.
