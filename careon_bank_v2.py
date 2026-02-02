import json
import os
from datetime import datetime
from typing import Any, Dict

def _default_bank() -> dict:
    return {
        "balance": 25,
        "sld_network_fund": 0,
        "history": [],  # list[dict]
    }

def _normalize(bank: dict) -> dict:
    if not isinstance(bank, dict):
        bank = {}

    bank.setdefault("balance", 25)
    bank.setdefault("sld_network_fund", 0)
    bank.setdefault("history", [])

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

    # Ensure all tx items are dict-ish; drop garbage
    cleaned = []
    for tx in bank["history"]:
        if isinstance(tx, dict) and "type" in tx and "amount" in tx:
            cleaned.append(tx)
    bank["history"] = cleaned

    return bank

def load_bank(path: str) -> dict:
    if not os.path.exists(path):
        return _default_bank()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _normalize(data)
    except Exception:
        return _default_bank()

def save_bank(bank: dict, path: str) -> None:
    bank = _normalize(bank)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2)

def ensure_bank_exists(path: str) -> dict:
    """Create a valid bank file if missing or corrupted."""
    b = load_bank(path)
    save_bank(b, path)
    return b

def summarize(bank: dict) -> str:
    return f"Balance: {bank.get('balance', 0)} Ȼ • 🌐 Fund: {bank.get('sld_network_fund', 0)} Ȼ"

def _log(bank: dict, t: str, amount: int, note: str) -> None:
    bank.setdefault("history", [])
    bank["history"].append({
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "type": t,
        "amount": int(amount),
        "note": note,
    })

def spend(bank: dict, cost: int, note: str = "spend") -> bool:
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
    return bank.get("history", [])[-keep:]