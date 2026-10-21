"""Report file sizes below a directory without following symlinks."""
from pathlib import Path


def largest_files(root: Path, limit: int = 10) -> list[tuple[int, Path]]:
    if limit < 1:
        raise ValueError("limit must be positive")
    files = ((p.stat(follow_symlinks=False).st_size, p) for p in root.rglob("*") if p.is_file() and not p.is_symlink())
    return sorted(files, reverse=True)[:limit]


if __name__ == "__main__":
    import sys
    base = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    for size, path in largest_files(base):
        print(f"{size:>10}  {path}")