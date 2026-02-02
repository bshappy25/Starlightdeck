"""SLD_Cleanv2.py

Starlight Deck (clean v2)

This version:
- Removes redundancy + dead/unreachable code from the prior merged file.
- Preserves your gameplay loop and the 3 Estrella AI moments:
  - After 10th draw: two paragraphs
  - After 20th draw: ratio/energy analysis
  - Then one final question with 5-line response
- Intentionally does NOT import Careon bank or user profile yet.
  We'll re-introduce those as clean modules after the core loop is stable.

Run:
  python SLD_Cleanv2.py

API key:
- Put your key in the API_KEY constant below, or
- Set environment variable STARLIGHT_API_KEY.

"""

from __future__ import annotations

import careon_bank_v2 as bank
import os
import user_profile as profile
import random
import time
from collections import Counter
from typing import Dict, Tuple

import requests
from colorama import Fore, Style, init

init(autoreset=True)

# =========================
# CONFIG
# =========================

# Prefer env var so you don't accidentally commit a key.
API_KEY = os.getenv("STARLIGHT_API_KEY")  # or paste here

# Gemini generateContent endpoint (matches your previous file)
MODEL_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

# If the user's optional question contains this character, we force a Zenith draw.
FORCE_ZENITH_SYMBOL = "â—‡"
ZENITH_CHANCE_PERCENT = 5

DRAW_10 = 10
DRAW_20 = 20

ESTRELLA = Fore.LIGHTMAGENTA_EX + "âœ¨ Estrella âœ¨" + Style.RESET_ALL

# =========================
# DECK DEFINITIONS
# =========================

CARDS: Dict[str, Dict[str, str]] = {
    "acuity": {"color": Fore.BLUE, "name": "ACUITY", "emoji": "ðŸ”µ"},
    "valor": {"color": Fore.RED, "name": "VALOR", "emoji": "ðŸ”´"},
    "variety": {"color": Fore.YELLOW, "name": "VARIETY", "emoji": "ðŸŸ¡"},
}

LEVELS: Dict[int, Dict[str, int | str]] = {
    1: {"name": "Common", "weight": 75},
    2: {"name": "Rare", "weight": 20},
    3: {"name": "Legendary", "weight": 5},
}

# =========================
# TEXT / FIELDS
# =========================

def get_vibe_fields(vibe: str, level: int, zenith: bool) -> Dict[str, str]:
    base = {
        "acuity": {
            1: ("Clarity", "Reduce noise.", "Truth over comfort."),
            2: ("Insight", "See structure.", "Depth and precision."),
            3: ("Revelation", "Cut illusion.", "Crystalline wisdom."),
        },
        "valor": {
            1: ("Courage", "Act once.", "Action beats fear."),
            2: ("Resolve", "Commit fully.", "Strength with purpose."),
            3: ("Command", "Lead boldly.", "Transform through will."),
        },
        "variety": {
            1: ("Play", "Try new paths.", "Curiosity first."),
            2: ("Surprise", "Break pattern.", "Creative risk."),
            3: ("Wonder", "Transcend limits.", "Reality bending."),
        },
    }

    intention, goal, value = base[vibe][level]

    if zenith:
        intention = f"ZENITH: {intention}"
        goal = "Focus intention."
        value = "Alignment creates power."

    return {
        "Intention": intention,
        "Personal goal": goal,
        "Affixing value": value,
    }

# =========================
# AI
# =========================

def _missing_key_message() -> str:
    return (
        "[AI disabled] No API key found.\n"
        "Set STARLIGHT_API_KEY in your environment or paste your key into API_KEY."
    )


def ask_ai(prompt: str, retries: int = 2) -> str:
    """Call Gemini generateContent and return plain text.\n\n    Cleaned:
    - no dead/unreachable code
    - defensive extraction of response
    - basic retry with backoff
    """

    if not API_KEY or "PASTE_" in API_KEY or "API key" in API_KEY:
        return _missing_key_message()

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY,
    }
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    last_err = None
    for attempt in range(retries + 1):
        try:
            r = requests.post(MODEL_URL, headers=headers, json=payload, timeout=(10, 90))
            if r.status_code != 200:
                # Keep error short (avoid dumping giant HTML)
                last_err = f"HTTP {r.status_code}: {r.text[:200]}"
            else:
                data = r.json()
                # Defensive extraction
                candidates = data.get("candidates") or []
                if not candidates:
                    return "[AI error] No candidates returned."

                content = candidates[0].get("content") or {}
                parts = content.get("parts") or []
                if not parts:
                    return "[AI error] No content parts returned."

                text = parts[0].get("text")
                return text if isinstance(text, str) and text.strip() else "[AI error] Empty text."

        except requests.exceptions.Timeout:
            last_err = "Timeout (API/network slow)."
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"

        time.sleep(0.8 * (attempt + 1))

    return f"[AI error] {last_err}"

# =========================
# DRAW LOGIC
# =========================

def draw_card() -> Tuple[str, int]:
    vibe = random.choice(list(CARDS.keys()))

    # Weighted roll based on LEVELS weights
    roll = random.randint(1, 100)
    cumulative = 0
    for lvl in sorted(LEVELS.keys()):
        cumulative += int(LEVELS[lvl]["weight"])  # type: ignore[index]
        if roll <= cumulative:
            return vibe, lvl

    # Fallback (should never happen if weights sum to 100)
    return vibe, 1


def zenith_check(forced: bool) -> Tuple[bool, bool]:
    """Returns (zenith, forced_flag)."""
    if forced:
        return True, True
    return (random.randint(1, 100) <= ZENITH_CHANCE_PERCENT), False


def bar(n: int, w: int = 20) -> str:
    return "â–ˆ" * min(n, w) + "â–‘" * max(0, w - n)

# =========================
# DISPLAY
# =========================

def display_card(vibe: str, level: int, zenith: bool, fields: Dict[str, str], stats: Dict) -> None:
    c = CARDS[vibe]

    print("\n" + "âœ¨" * 30)
    print(Fore.MAGENTA + "ðŸŒŸ STARLIGHT DECK ðŸŒŸ" + Style.RESET_ALL)
    print("âœ¨" * 30)

    vc = stats["vibe"]
    print(Fore.BLUE + f"ðŸ”µ {bar(vc['acuity'])} {vc['acuity']}")
    print(Fore.RED + f"ðŸ”´ {bar(vc['valor'])} {vc['valor']}")
    print(Fore.YELLOW + f"ðŸŸ¡ {bar(vc['variety'])} {vc['variety']}")

    z = "â—‡ ZENITH â—‡" if zenith else ""
    print(c["color"] + "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—")
    print(c["color"] + f"â•‘   {c['emoji']}  {c['name']:^18} â•‘")
    print(c["color"] + f"â•‘   Level {level} - {str(LEVELS[level]['name']):^12}  â•‘")
    print(c["color"] + f"â•‘   {z:^26} â•‘")
    print(c["color"] + "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" + Style.RESET_ALL)

    print()
    for k, v in fields.items():
        print(c["color"] + f"{k}:" + Style.RESET_ALL, Fore.WHITE + v)

# =========================
# AI EVENTS
# =========================

def estrella_10(stats: Dict) -> None:
    print("\n" + ESTRELLA)
    print(Fore.LIGHTMAGENTA_EX + "10-Draw Check-In\n" + Style.RESET_ALL)
    prompt = (
        "Write TWO short paragraphs reflecting on this 10-draw session so far. "
        "Keep it direct and emotionally grounded.\n\n"
        f"Vibes: {dict(stats['vibe'])}\n"
        f"Levels: {dict(stats['level'])}\n"
        f"Zenith count: {stats['zenith']} (forced {stats['zenith_forced']})"
    )
    print(Fore.WHITE + ask_ai(prompt))


def estrella_20(stats: Dict) -> None:
    print("\n" + ESTRELLA)
    print(Fore.LIGHTMAGENTA_EX + "20-Draw Ratio & Energy Analysis\n" + Style.RESET_ALL)
    prompt = (
        "Write TWO short paragraphs.\n"
        "Paragraph 1: analyze the vibe ratios and what they imply.\n"
        "Paragraph 2: describe the session's overall energy (high/medium/low) with one suggestion.\n\n"
        f"Vibes: {dict(stats['vibe'])}\n"
        f"Levels: {dict(stats['level'])}\n"
        f"Zenith count: {stats['zenith']} (forced {stats['zenith_forced']})"
    )
    print(Fore.WHITE + ask_ai(prompt))


def estrella_final(stats: Dict) -> None:
    fq = input(Fore.CYAN + "\nFinal question for Estrella: " + Style.RESET_ALL)
    print("\n" + ESTRELLA)

    cleaned_q = fq.replace(FORCE_ZENITH_SYMBOL, "").strip()
    final_prompt = (
        "Return EXACTLY five lines, exactly in this format:\n"
        "Intention: ...\n"
        "Forward action: ...\n"
        "Past reflection: ...\n"
        "Energy level: ...\n"
        "Aspirational message: ...\n\n"
        f"Session stats: {stats}\n"
        f"Question: {cleaned_q}"
    )

    print(Fore.WHITE + ask_ai(final_prompt))

# =========================
# MAIN
# =========================

def new_stats() -> Dict:
    return {
        "draws": 0,
        "vibe": Counter({"acuity": 0, "valor": 0, "variety": 0}),
        "level": Counter({1: 0, 2: 0, 3: 0}),
        "zenith": 0,
        "zenith_forced": 0,
    }

HERE = os.path.dirname(os.path.abspath(__file__))

PROFILE_PATH = os.path.join(HERE, "user_profile.json")

BANK_PATH = os.path.join(HERE, "careon_bank_v2.json")



def estrella_input(prompt: str, b: dict) -> str:
    """
    Only Estrella interactions can accept TGIF.
    If TGIF is entered, we apply +5 and re-prompt.
    """
    while True:
        s = input(prompt)

        applied, msg = bank.try_apply_devtool(s, b)
        if applied:
            print(msg)
            bank.save_bank(b, BANK_PATH)
            continue

        return s


def run() -> None:
    # --- User Profile ---
    p = profile.get_or_create_profile_interactive(PROFILE_PATH)
    print(profile.summarize(p))

    # --- Careon Bank ---
    b = bank.load_bank(BANK_PATH)
    print(bank.summarize(b))

    # Optional: daily bonus
    if bank.check_daily_bonus(b):
        print("âœ¨ Daily bonus: +10 È»")
        bank.save_bank(b, BANK_PATH)
        print(bank.summarize(b))

    # Charge to start the round
    if not bank.charge_round(b, cost=1):
        print("Not enough Careons to start a round.")
        print(bank.summarize(b))
        return

    bank.save_bank(b, BANK_PATH)
    print("ðŸŽŸï¸ Round started (-1 È»)")
    print(bank.summarize(b))

    # --- continue game setup below ---



    stats = new_stats()

    print(Fore.CYAN + "\nðŸŒŸ Starlight Deck ready.\n" + Style.RESET_ALL)
    print(
        Fore.CYAN
        + "Controls: Enter THREE SPACES then Enter to draw."
        + Style.RESET_ALL
    )
    print(
        Fore.CYAN
        + f"Optional: include {FORCE_ZENITH_SYMBOL} in your question to force Zenith."
        + Style.RESET_ALL
    )

    while True:
        gate = input(Fore.CYAN + "\nEnter THREE SPACES then Enter to draw: " + Style.RESET_ALL)
        if gate != "   ":
            continue

        vibe, level = draw_card()
        stats["draws"] += 1
        stats["vibe"][vibe] += 1
        stats["level"][level] += 1

        q = input(
            Fore.CYAN
            + f"Ask (optional, add {FORCE_ZENITH_SYMBOL} to force Zenith): "
            + Style.RESET_ALL
        )
        forced = FORCE_ZENITH_SYMBOL in q
        zenith, forced_flag = zenith_check(forced)

        if zenith:
            stats["zenith"] += 1
        if forced_flag:
            stats["zenith_forced"] += 1

        fields = get_vibe_fields(vibe, level, zenith)
        display_card(vibe, level, zenith, fields, stats)

        # ===== AI EVENTS (exactly three times) =====
        if stats["draws"] == DRAW_10:
            estrella_10(stats)

        if stats["draws"] == DRAW_20:
            estrella_20(stats)
            estrella_final(stats)

            end = input(Fore.CYAN + "\nRestart? (y/n): " + Style.RESET_ALL).lower().strip()
            if end == "y":
                stats = new_stats()
                continue

            print(Fore.CYAN + "\nGoodbye.\n" + Style.RESET_ALL)
            return


if __name__ == "__main__":
    run()