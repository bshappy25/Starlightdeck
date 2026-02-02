import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


# ----------------------------
# Defaults + normalization
# ----------------------------

def _default_bank() -> dict:
    return {
        "balance": 25,
        "sld_network_fund": 0,
        "history": [],  # list[dict]
        "meta": {
            "schema": 1,
            "last_saved_utc": None,
        },
    }


def _normalize(bank: dict) -> dict:
    if not isinstance(bank, dict):
        bank = {}

    bank.setdefault("balance", 25)
    bank.setdefault("sld_network_fund", 0)
    bank.setdefault("history", [])
    bank.setdefault("meta", {})

    # ints
    try:
        bank["balance"] = int(bank["balance"])
    except Exception:
        bank["balance"] = 25

    try:
        bank["sld_network_fund"] = int(bank["sld_network_fund"])
    except Exception:
        bank["sld_network_fund"] = 0

    if not isinstance(bank["history"], list):
        bank["history"] = []

    # meta safety
    if not isinstance(bank["meta"], dict):
        bank["meta"] = {}
    bank["meta"].setdefault("schema", 1)
    bank["meta"].setdefault("last_saved_utc", None)

    # Ensure all tx items are dict-ish; drop garbage
    cleaned = []
    for tx in bank["history"]:
        if isinstance(tx, dict) and "type" in tx and "amount" in tx and "ts" in tx:
            cleaned.append(tx)
    bank["history"] = cleaned

    # optional: keep history from growing forever (safe cap)
    # if you want unlimited, delete this.
    MAX_HISTORY = 5000
    if len(bank["history"]) > MAX_HISTORY:
        bank["history"] = bank["history"][-MAX_HISTORY:]

    return bank


# ----------------------------
# Atomic file ops (stability)
# ----------------------------

def _read_json(path: str) -> Optional[dict]:
    """Return dict if read succeeds, else None."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _atomic_save_json(data: dict, path: str) -> None:
    """
    Atomic write with backup:
    - writes to .tmp
    - rotates existing file to .bak
    - replaces final path atomically
    """
    folder = os.path.dirname(path) or "."
    os.makedirs(folder, exist_ok=True)

    tmp = path + ".tmp"
    bak = path + ".bak"

    # write tmp
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # rotate current -> bak (best effort)
    if os.path.exists(path):
        try:
            os.replace(path, bak)
        except Exception:
            pass

    # promote tmp -> final
    os.replace(tmp, path)


# ----------------------------
# Public API
# ----------------------------

def load_bank(path: str) -> dict:
    """
    Load bank safely.
    Recovery order:
      1) path
      2) path.bak
      3) default
    """
    if os.path.exists(path):
        data = _read_json(path)
        if isinstance(data, dict):
            return _normalize(data)

    bak = path + ".bak"
    if os.path.exists(bak):
        data = _read_json(bak)
        if isinstance(data, dict):
            return _normalize(data)

    return _default_bank()


def save_bank(bank: dict, path: str) -> None:
    bank = _normalize(bank)
    bank["meta"]["last_saved_utc"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    _atomic_save_json(bank, path)


def ensure_bank_exists(path: str) -> dict:
    """Create a valid bank file if missing or corrupted."""
    b = load_bank(path)
    save_bank(b, path)
    return b


def summarize(bank: dict) -> str:
    bank = _normalize(bank)
    return f"Balance: {bank.get('balance', 0)} Ȼ • 🌐 Fund: {bank.get('sld_network_fund', 0)} Ȼ"


def _log(bank: dict, t: str, amount: int, note: str) -> None:
    bank.setdefault("history", [])
    bank["history"].append({
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "type": t,
        "amount": int(amount),
        "note": str(note),
    })


def spend(bank: dict, cost: int, note: str = "spend") -> bool:
    """
    Spend decreases user balance and increases network fund.
    """
    bank = _normalize(bank)
    cost = int(cost)
    if cost <= 0:
        return True
    if bank["balance"] < cost:
        return False

    bank["balance"] -= cost
    bank["sld_network_fund"] += cost  # ALL spend funds the network
    _log(bank, "spend", cost, note)
    return True


def earn(bank: dict, amount: int, note: str = "earn") -> None:
    """
    Earn increases user balance.
    """
    bank = _normalize(bank)
    amount = int(amount)
    if amount <= 0:
        return

    bank["balance"] += amount
    _log(bank, "earn", amount, note)


def award_once_per_round(bank: dict, note: str, amount: int) -> bool:
    """
    Award once since the last 'spend' tx.
    If an earn tx with same note already exists after the last spend, do nothing.
    """
    bank = _normalize(bank)

    for tx in reversed(bank.get("history", [])):
        if tx.get("type") == "spend":
            break
        if tx.get("type") == "earn" and tx.get("note") == note:
            return False

    earn(bank, amount, note)
    return True


def recent_txs(bank: dict, keep: int = 12) -> list:
    bank = _normalize(bank)
    keep = max(0, int(keep))
    return bank.get("history", [])[-keep:]


# ----------------------------
# Optional: export/import helpers
# (for persistence across Streamlit restarts)
# ----------------------------

def export_bank_json(bank: dict) -> str:
    """Return JSON string suitable for download/backup."""
    bank = _normalize(bank)
    return json.dumps(bank, indent=2, ensure_ascii=False)


def import_bank_json(json_text: str) -> dict:
    """Parse JSON text, normalize, return bank dict (does not save)."""
    try:
        data = json.loads(json_text)
        if isinstance(data, dict):
            return _normalize(data)
    except Exception:
        pass
    return _default_bank()
