import json
import os
import secrets
import string
from datetime import datetime
from typing import Optional, Dict, Any


# ----------------------------
# Defaults + normalization
# ----------------------------

def _default_ledger() -> dict:
    return {
        "codes": {},  # code -> {value:int, created_utc:str, created_by:str, redeemed_utc:str|None, redeemed_by:str|None, note:str}
        "history": [],  # list of events
        "meta": {
            "schema": 1,
            "last_saved_utc": None,
        },
    }


def _normalize(ledger: dict) -> dict:
    if not isinstance(ledger, dict):
        ledger = {}

    ledger.setdefault("codes", {})
    ledger.setdefault("history", [])
    ledger.setdefault("meta", {})

    if not isinstance(ledger["codes"], dict):
        ledger["codes"] = {}
    if not isinstance(ledger["history"], list):
        ledger["history"] = []
    if not isinstance(ledger["meta"], dict):
        ledger["meta"] = {}

    ledger["meta"].setdefault("schema", 1)
    ledger["meta"].setdefault("last_saved_utc", None)

    # Normalize codes entries
    cleaned_codes = {}
    for code, info in ledger["codes"].items():
        if not isinstance(code, str) or not code.strip():
            continue
        if not isinstance(info, dict):
            continue

        value = info.get("value", 0)
        try:
            value = int(value)
        except Exception:
            value = 0

        cleaned_codes[code.strip()] = {
            "value": value,
            "created_utc": str(info.get("created_utc") or ""),
            "created_by": str(info.get("created_by") or ""),
            "redeemed_utc": info.get("redeemed_utc", None),
            "redeemed_by": info.get("redeemed_by", None),
            "note": str(info.get("note") or ""),
        }

    ledger["codes"] = cleaned_codes

    # Clean history
    cleaned_hist = []
    for evt in ledger["history"]:
        if isinstance(evt, dict) and "ts" in evt and "type" in evt:
            cleaned_hist.append(evt)
    ledger["history"] = cleaned_hist

    # cap history to prevent bloat
    MAX_HISTORY = 5000
    if len(ledger["history"]) > MAX_HISTORY:
        ledger["history"] = ledger["history"][-MAX_HISTORY:]

    return ledger


# ----------------------------
# Atomic file ops
# ----------------------------

def _read_json(path: str) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _atomic_save_json(data: dict, path: str) -> None:
    folder = os.path.dirname(path) or "."
    os.makedirs(folder, exist_ok=True)

    tmp = path + ".tmp"
    bak = path + ".bak"

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if os.path.exists(path):
        try:
            os.replace(path, bak)
        except Exception:
            pass

    os.replace(tmp, path)


# ----------------------------
# Public: load/save
# ----------------------------

def load_ledger(path: str) -> dict:
    if os.path.exists(path):
        data = _read_json(path)
        if isinstance(data, dict):
            return _normalize(data)

    bak = path + ".bak"
    if os.path.exists(bak):
        data = _read_json(bak)
        if isinstance(data, dict):
            return _normalize(data)

    return _default_ledger()


def save_ledger(ledger: dict, path: str) -> None:
    ledger = _normalize(ledger)
    ledger["meta"]["last_saved_utc"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    _atomic_save_json(ledger, path)


def ensure_ledger_exists(path: str) -> dict:
    l = load_ledger(path)
    save_ledger(l, path)
    return l


# ----------------------------
# Code generation + logging
# ----------------------------

def _now_utc() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _log(ledger: dict, t: str, payload: dict) -> None:
    ledger.setdefault("history", [])
    ledger["history"].append({
        "ts": _now_utc(),
        "type": t,
        **payload,
    })


def generate_code(prefix: str = "SLD", length: int = 8) -> str:
    """
    Generates codes like: SLD-AB12CD34
    Uses a cryptographically strong generator (secrets).
    """
    alphabet = string.ascii_uppercase + string.digits
    chunk = "".join(secrets.choice(alphabet) for _ in range(length))
    prefix = (prefix or "SLD").upper().strip()
    return f"{prefix}-{chunk}"


# ----------------------------
# Mint + Redeem
# ----------------------------

def mint_code(ledger: dict, value: int, created_by: str = "admin", note: str = "", prefix: str = "SLD") -> str:
    """
    Create a new redeemable code worth `value` tokens.
    """
    ledger = _normalize(ledger)
    value = int(value)

    if value <= 0:
        raise ValueError("value must be positive")

    # Ensure uniqueness
    code = generate_code(prefix=prefix)
    while code in ledger["codes"]:
        code = generate_code(prefix=prefix)

    ledger["codes"][code] = {
        "value": value,
        "created_utc": _now_utc(),
        "created_by": str(created_by),
        "redeemed_utc": None,
        "redeemed_by": None,
        "note": str(note),
    }
    _log(ledger, "mint", {"code": code, "value": value, "created_by": created_by, "note": note})
    return code


def is_redeemed(ledger: dict, code: str) -> bool:
    ledger = _normalize(ledger)
    info = ledger["codes"].get((code or "").strip().upper())
    if not info:
        return False
    return bool(info.get("redeemed_utc"))


def redeem_code(ledger: dict, code: str, redeemed_by: str = "user") -> int:
    """
    Redeems a code if valid and unused.
    Returns value to award.
    Raises ValueError if invalid or already redeemed.
    """
    ledger = _normalize(ledger)
    code_key = (code or "").strip().upper()

    if not code_key:
        raise ValueError("empty code")

    info = ledger["codes"].get(code_key)
    if not info:
        raise ValueError("invalid code")

    if info.get("redeemed_utc"):
        raise ValueError("code already redeemed")

    value = int(info.get("value", 0))
    info["redeemed_utc"] = _now_utc()
    info["redeemed_by"] = str(redeemed_by)

    _log(ledger, "redeem", {"code": code_key, "value": value, "redeemed_by": redeemed_by})
    return value


def recent_events(ledger: dict, keep: int = 12) -> list:
    ledger = _normalize(ledger)
    keep = max(0, int(keep))
    return ledger.get("history", [])[-keep:]


# ----------------------------
# Purchase helper (your network rule)
# ----------------------------

def compute_network_cut(tokens_purchased: int) -> int:
    """
    Rule: Every 100 tokens purchased, 5 go to the network fund.
    Examples:
      100 -> 5
      199 -> 5
      200 -> 10
      50  -> 0
    """
    tokens_purchased = int(tokens_purchased)
    if tokens_purchased <= 0:
        return 0
    return (tokens_purchased // 100) * 5


# ----------------------------
# Optional: export/import
# ----------------------------

def export_ledger_json(ledger: dict) -> str:
    ledger = _normalize(ledger)
    return json.dumps(ledger, indent=2, ensure_ascii=False)


def import_ledger_json(json_text: str) -> dict:
    try:
        data = json.loads(json_text)
        if isinstance(data, dict):
            return _normalize(data)
    except Exception:
        pass
    return _default_ledger()
