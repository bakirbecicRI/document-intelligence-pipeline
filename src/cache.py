import hashlib
import json
from pathlib import Path
from typing import Dict, Any


def compute_file_hash(path: str) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cache(cache_path: str) -> Dict[str, Any]:
    p = Path(cache_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if not p.exists():
        # inicijalno prazan cache
        p.write_text("{}", encoding="utf-8")
        return {}

    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        # ako se pokvario file, ne crashaj demo
        return {}


def save_cache(cache: Dict[str, Any], cache_path: str) -> None:
    p = Path(cache_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
