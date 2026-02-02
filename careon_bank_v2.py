import json
import os
from datetime import datetime

def _default_bank():
    return {
        "balance": 25,
        "sld_network_fund": 0,
        "history": [],
    }

def load_bank(path: str) -> dict:
    if not os.path.exists(path):
        return _default_bank()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return _default_bank()
        # normalize
        data.setdefault("balance", 25)
        data.setdefault("sld_network_fund", 0)
        data.setdefault("history", [])
        data["balance"] = int(data["balance"])
        data["sld_network_fund"] = int(data["sld_network_fund"])
        if not isinstance(data["history"], list):
            data["history"] = []
        return data
    except Exception:
        return _default_bank()

def save_bank(bank: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2)

def summarize(bank: dict) -> str:
    return f"Balance: {bank.get('balance', 0)} Ȼ • 🌐 Fund: {bank.get('sld_network_fund', 0)} Ȼ"

def _log(bank: dict, t: str, amount: int, note: str):
    bank["history"].append({
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "type": t,
        "amount": int(amount),
        "note": note,
    })

def spend(bank: dict, cost: int, note: str = "spend") -> bool:
    cost = int(cost)
    if bank["balance"] < cost:
        return False
    bank["balance"] -= cost
    bank["sld_network_fund"] += cost  # ALL spend funds the network
    _log(bank, "spend", cost, note)
    return True

def earn(bank: dict, amount: int, note: str = "earn") -> None:
    amount = int(amount)
    bank["balance"] += amount
    _log(bank, "earn", amount, note)

def award_once_per_round(bank: dict, note: str, amount: int) -> bool:
    # Prevent double awarding since last spend
    for tx in reversed(bank.get("history", [])):
        if tx.get("type") == "spend":
            break
        if tx.get("type") == "earn" and tx.get("note") == note:
            return False
    earn(bank, amount, note)
    return True