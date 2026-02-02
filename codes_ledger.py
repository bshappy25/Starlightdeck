import json
import os
import secrets
import string
import time
from typing import Dict, Any, Tuple


def _now() -> int:
    return int(time.time())


def ledger_path(here: str) -> str:
    return os.path.join(here, "codes_ledger.json")


def load_ledger(path: str) -> Dict[str, Any]:
    """
    Ledger format:
    {
      "codes": {
        "DEP-50-ABC123": {"amount": 50, "created_at": 170..., "redeemed_at": null, "redeemed_by": null}
      }
    }
    """
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
        # If corrupted, don’t crash the app — start a fresh ledger
        return {"codes": {}}


def save_ledger(data: Dict[str, Any], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _random_chunk(n: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def generate_deposit_code(amount: int, existing_codes: set[str]) -> str:
    """
    Creates a human-friendly unique code like:
      DEP-50-AB12CD
    """
    amount = int(amount)
    for _ in range(50):
        code = f"DEP-{amount}-{_random_chunk(6)}"
        if code not in existing_codes:
            return code
    # Extremely unlikely fallback
    return f"DEP-{amount}-{_random_chunk(10)}"


def add_code(path: str, amount: int) -> str:
    data = load_ledger(path)
    codes = data["codes"]
    code = generate_deposit_code(int(amount), set(codes.keys()))
    codes[code] = {
        "amount": int(amount),
        "created_at": _now(),
        "redeemed_at": None,
        "redeemed_by": None,
    }
    save_ledger(data, path)
    return code


def redeem_code(path: str, code_raw: str, redeemer: str = "web") -> Tuple[bool, str, int]:
    """
    Returns: (ok, message, amount)
    If ok is True, amount is the deposit amount.
    """
    code = (code_raw or "").strip().upper()
    if not code:
        return False, "Enter a code.", 0

    data = load_ledger(path)
    codes = data["codes"]

    if code not in codes:
        return False, "Invalid code.", 0

    entry = codes[code]
    if entry.get("redeemed_at"):
        return False, "Code already redeemed.", 0

    amount = int(entry.get("amount", 0))
    if amount <= 0:
        return False, "Code amount invalid.", 0

    entry["redeemed_at"] = _now()
    entry["redeemed_by"] = redeemer
    save_ledger(data, path)
    return True, "Redeemed successfully.", amount