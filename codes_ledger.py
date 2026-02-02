import json
import os
import secrets
from datetime import datetime

def _load(path: str) -> dict:
    if not os.path.exists(path):
        return {"codes": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"codes": {}}
        data.setdefault("codes", {})
        if not isinstance(data["codes"], dict):
            data["codes"] = {}
        return data
    except Exception:
        return {"codes": {}}

def _save(data: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def add_code(path: str, amount: int) -> str:
    """
    Create a one-time deposit code: DEP-<AMT>-<TOKEN>
    """
    amount = int(amount)
    if amount <= 0:
        raise ValueError("Amount must be > 0")

    data = _load(path)

    token = secrets.token_hex(3).upper()  # 6 hex chars
    code = f"DEP-{amount}-{token}"

    # ensure unique
    while code in data["codes"]:
        token = secrets.token_hex(3).upper()
        code = f"DEP-{amount}-{token}"

    data["codes"][code] = {
        "amount": amount,
        "created_ts": _now(),
        "redeemed_ts": None,
        "redeemer": None,
    }
    _save(data, path)
    return code

def redeem_code(path: str, code: str, redeemer: str = "web"):
    """
    Returns (ok, msg, amount)
    """
    code = (code or "").strip().upper()
    if not code.startswith("DEP-"):
        return (False, "Invalid code format.", 0)

    data = _load(path)
    row = data["codes"].get(code)
    if not row:
        return (False, "Code not found.", 0)

    if row.get("redeemed_ts"):
        return (False, "Code already redeemed.", 0)

    amount = int(row.get("amount", 0))
    if amount <= 0:
        return (False, "Corrupted code amount.", 0)

    row["redeemed_ts"] = _now()
    row["redeemer"] = redeemer
    data["codes"][code] = row
    _save(data, path)

    return (True, "Code redeemed.", amount)