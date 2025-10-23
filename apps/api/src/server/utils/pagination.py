import base64, json
from datetime import datetime

def encode_token(ts_iso: str) -> str:
    return base64.urlsafe_b64encode(json.dumps({"ts": ts_iso}).encode()).decode()

def decode_token(token: str) -> str:
    data = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
    return data["ts"]