#!/usr/bin/env python3
"""Print section names and key names from an INI file."""
import argparse
import configparser
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    config = configparser.ConfigParser()
    if not config.read(args.config, encoding="utf-8"):
        parser.error(f"could not read configuration: {args.config}")
    for section in config.sections():
        print(f"[{section}] ({len(config[section])} keys)")
        for key in config[section]:
            print(f"  {key}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
