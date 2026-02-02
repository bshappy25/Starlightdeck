import json
import os
import re
from datetime import datetime
from typing import Optional


# ----------------------------
# Defaults + normalization
# ----------------------------

def _default_store() -> dict:
    return {
        "profiles": {},  # user_id -> profile dict
        "meta": {
            "schema": 1,
            "last_saved_utc": None,
        }
    }


def _now_utc() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _sanitize_user_id(raw: str) -> str:
    raw = (raw or "").strip().lower()
    raw = re.sub(r"[^a-z0-9_\-]", "", raw)
    return raw or "guest"


def _default_profile(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "display_name": user_id,
        "role": "player",  # "player" or "admin"
        "created_utc": _now_utc(),
        "last_seen_utc": _now_utc(),
        "stats": {
            "rounds_started": 0,
            "normal_completions": 0,
            "rapid_runs": 0,
            "codes_redeemed": 0,
        },
        "prefs": {
            "theme": "dark",
            "audio_on": False,
        },
        "notes": "",
    }


def _normalize_store(store: dict) -> dict:
    if not isinstance(store, dict):
        store = {}

    store.setdefault("profiles", {})
    store.setdefault("meta", {})

    if not isinstance(store["profiles"], dict):
        store["profiles"] = {}
    if not isinstance(store["meta"], dict):
        store["meta"] = {}

    store["meta"].setdefault("schema", 1)
    store["meta"].setdefault("last_saved_utc", None)

    # normalize each profile
    cleaned = {}
    for uid, prof in store["profiles"].items():
        if not isinstance(uid, str):
            continue
        uid2 = _sanitize_user_id(uid)
        if not isinstance(prof, dict):
            prof = _default_profile(uid2)

        prof.setdefault("user_id", uid2)
        prof.setdefault("display_name", uid2)
        prof.setdefault("role", "player")
        prof.setdefault("created_utc", _now_utc())
        prof.setdefault("last_seen_utc", _now_utc())
        prof.setdefault("stats", {})
        prof.setdefault("prefs", {})
        prof.setdefault("notes", "")

        if not isinstance(prof["stats"], dict):
            prof["stats"] = {}
        if not isinstance(prof["prefs"], dict):
            prof["prefs"] = {}

        # stats keys
        prof["stats"].setdefault("rounds_started", 0)
        prof["stats"].setdefault("normal_completions", 0)
        prof["stats"].setdefault("rapid_runs", 0)
        prof["stats"].setdefault("codes_redeemed", 0)

        # ensure ints
        for k in ["rounds_started", "normal_completions", "rapid_runs", "codes_redeemed"]:
            try:
                prof["stats"][k] = int(prof["stats"].get(k, 0))
            except Exception:
                prof["stats"][k] = 0

        # prefs keys
        theme = str(prof["prefs"].get("theme", "dark")).lower().strip()
        prof["prefs"]["theme"] = theme if theme in ("dark", "light") else "dark"
        prof["prefs"]["audio_on"] = bool(prof["prefs"].get("audio_on", False))

        # role
        role = str(prof.get("role", "player")).lower().strip()
        prof["role"] = role if role in ("player", "admin") else "player"

        # display name
        prof["display_name"] = str(prof.get("display_name") or uid2).strip()[:40] or uid2

        cleaned[uid2] = prof

    store["profiles"] = cleaned
    return store


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
# Public API
# ----------------------------

def load_store(path: str) -> dict:
    if os.path.exists(path):
        data = _read_json(path)
        if isinstance(data, dict):
            return _normalize_store(data)

    bak = path + ".bak"
    if os.path.exists(bak):
        data = _read_json(bak)
        if isinstance(data, dict):
            return _normalize_store(data)

    return _default_store()


def save_store(store: dict, path: str) -> None:
    store = _normalize_store(store)
    store["meta"]["last_saved_utc"] = _now_utc()
    _atomic_save_json(store, path)


def get_or_create_profile(store: dict, user_id: str) -> dict:
    store = _normalize_store(store)
    uid = _sanitize_user_id(user_id)

    prof = store["profiles"].get(uid)
    if not prof:
        prof = _default_profile(uid)
        store["profiles"][uid] = prof

    # update last seen
    prof["last_seen_utc"] = _now_utc()
    return prof


def set_role(store: dict, user_id: str, role: str) -> None:
    prof = get_or_create_profile(store, user_id)
    role = (role or "").strip().lower()
    prof["role"] = "admin" if role == "admin" else "player"


def bump_stat(store: dict, user_id: str, key: str, amount: int = 1) -> None:
    prof = get_or_create_profile(store, user_id)
    prof.setdefault("stats", {})
    try:
        prof["stats"][key] = int(prof["stats"].get(key, 0)) + int(amount)
    except Exception:
        prof["stats"][key] = 0


def set_pref(store: dict, user_id: str, key: str, value) -> None:
    prof = get_or_create_profile(store, user_id)
    prof.setdefault("prefs", {})
    prof["prefs"][key] = value


def summarize_profile(profile: dict) -> str:
    uid = profile.get("user_id", "guest")
    name = profile.get("display_name", uid)
    role = profile.get("role", "player")
    s = profile.get("stats", {})
    return (
        f"User: {name} ({uid}) • role: {role}\n"
        f"Rounds started: {s.get('rounds_started',0)} • "
        f"Normal completions: {s.get('normal_completions',0)} • "
        f"Rapid runs: {s.get('rapid_runs',0)} • "
        f"Codes redeemed: {s.get('codes_redeemed',0)}"
    )


# ----------------------------
# Optional: export/import
# ----------------------------

def export_store_json(store: dict) -> str:
    store = _normalize_store(store)
    return json.dumps(store, indent=2, ensure_ascii=False)


def import_store_json(json_text: str) -> dict:
    try:
        data = json.loads(json_text)
        if isinstance(data, dict):
            return _normalize_store(data)
    except Exception:
        pass
    return _default_store()
