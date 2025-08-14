import hashlib
from pathlib import Path

def replay_hash(config_path: str, data_paths: list[str]) -> str:
    h = hashlib.sha256()
    h.update(Path(config_path).read_bytes())
    for d in data_paths:
        h.update(Path(d).read_bytes())
    return h.hexdigest()[:12]
