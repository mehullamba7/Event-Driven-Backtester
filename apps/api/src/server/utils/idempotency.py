import hashlib, json

def run_hash(payload: dict) -> str:
    """Stable hash for idempotency of CreateRunRequest."""
    # Sort keys to guarantee stable JSON
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()