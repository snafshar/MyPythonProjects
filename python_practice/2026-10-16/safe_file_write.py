"""Write text through a temporary sibling file before replacing the target."""
from pathlib import Path
import os
import tempfile

def atomic_write_text(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent,
                                         delete=False) as stream:
            temporary_name = stream.name
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, target)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)

if __name__ == "__main__":
    print("Import atomic_write_text(path, text) to use this helper.")
