from __future__ import annotations

import random
from collections import Counter
from typing import Dict, Tuple, Optional

# ===========
# CONFIG
# ===========

FORCE_ZENITH_SYMBOL = "◇"  # Use clean UTF-8 symbol
ZENITH_CHANCE_PERCENT = 5

DRAW_10 = 10
DRAW_20 = 20

# ===========
# DECK
# ===========

CARDS: Dict[str, Dict[str, str]] = {
    "acuity": {"name": "ACUITY", "emoji": "🔵"},
    "valor": {"name": "VALOR", "emoji": "🔴"},
    "variety": {"name": "VARIETY", "emoji": "🟡"},
}

LEVELS: Dict[int, Dict[str, int | str]] = {
    1: {"name": "Common", "weight": 75},
    2: {"name": "Rare", "weight": 20},
    3: {"name": "Legendary", "weight": 5},
}

# ===========
# TEXT / FIELDS
# ===========

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

# ===========
# DRAW LOGIC
# ===========

def draw_card() -> Tuple[str, int]:
    vibe = random.choice(list(CARDS.keys()))

    roll = random.randint(1, 100)
    cumulative = 0
    for lvl in sorted(LEVELS.keys()):
        cumulative += int(LEVELS[lvl]["weight"])  # type: ignore[index]
        if roll <= cumulative:
            return vibe, lvl

    return vibe, 1

def zenith_check(forced: bool) -> Tuple[bool, bool]:
    """Returns (zenith, forced_flag)."""
    if forced:
        return True, True
    return (random.randint(1, 100) <= ZENITH_CHANCE_PERCENT), False

# ===========
# STATS
# ===========

def new_stats() -> Dict:
    return {
        "draws": 0,
        "vibe": Counter({"acuity": 0, "valor": 0, "variety": 0}),
        "level": Counter({1: 0, 2: 0, 3: 0}),
        "zenith": 0,
        "zenith_forced": 0,
    }

# ===========
# DISPLAY (WEB)
# ===========

def bar(n: int, w: int = 20) -> str:
    # Simple text bar (Streamlit-safe)
    return "█" * min(n, w) + "░" * max(0, w - n)

def render_card_text(i: int, vibe: str, level: int, zenith: bool, fields: Dict[str, str], stats: Dict) -> str:
    c = CARDS[vibe]
    z = "◇ ZENITH ◇" if zenith else ""

    vc = stats["vibe"]
    lvlname = str(LEVELS[level]["name"])

    lines = []
    lines.append("✦" * 30)
    lines.append("STARLIGHT DECK")
    lines.append("✦" * 30)
    lines.append(f"Card #{i}")
    lines.append("")
    lines.append(f"🔵 {bar(vc['acuity'])} {vc['acuity']}")
    lines.append(f"🔴 {bar(vc['valor'])}  {vc['valor']}")
    lines.append(f"🟡 {bar(vc['variety'])} {vc['variety']}")
    lines.append("")
    lines.append(f"{c['emoji']} {c['name']} | Level {level} - {lvlname}  {z}".rstrip())
    lines.append("-" * 30)

    for k, v in fields.items():
        lines.append(f"{k}: {v}")

    return "\n".join(lines)

# ===========
# “AUTHENTIC” NORMAL TURN
# ===========

def normal_draw_step(stats: Dict, user_question: str) -> Dict:
    """
    Mirrors your CLI loop:
    - user can type a question (optional)
    - include FORCE_ZENITH_SYMBOL to force Zenith
    - draw vibe/level
    - zenith check
    - compute fields
    - update stats
    - return a draw record
    """
    vibe, level = draw_card()

    stats["draws"] += 1
    stats["vibe"][vibe] += 1
    stats["level"][level] += 1

    forced = FORCE_ZENITH_SYMBOL in (user_question or "")
    zenith, forced_flag = zenith_check(forced)

    if zenith:
        stats["zenith"] += 1
    if forced_flag:
        stats["zenith_forced"] += 1

    fields = get_vibe_fields(vibe, level, zenith)

    return {
        "vibe": vibe,
        "level": level,
        "zenith": zenith,
        "fields": fields,
        "question": (user_question or "").strip(),
        "forced": forced,
    }

def estrella_prompt_10(stats: Dict) -> str:
    # Matches your “two paragraphs” vibe
    return (
        "✨ Estrella ✨\n"
        "10-Draw Check-In\n\n"
        "Write TWO short paragraphs reflecting on this 10-draw session so far. "
        "Keep it direct and emotionally grounded.\n\n"
        f"Vibes: {dict(stats['vibe'])}\n"
        f"Levels: {dict(stats['level'])}\n"
        f"Zenith count: {stats['zenith']} (forced {stats['zenith_forced']})"
    )

def estrella_prompt_20(stats: Dict) -> str:
    return (
        "✨ Estrella ✨\n"
        "20-Draw Ratio & Energy Analysis\n\n"
        "Write TWO short paragraphs.\n"
        "Paragraph 1: analyze the vibe ratios and what they imply.\n"
        "Paragraph 2: describe the session's overall energy (high/medium/low) with one suggestion.\n\n"
        f"Vibes: {dict(stats['vibe'])}\n"
        f"Levels: {dict(stats['level'])}\n"
        f"Zenith count: {stats['zenith']} (forced {stats['zenith_forced']})"
    )

def estrella_final_template(stats: Dict, final_question: str) -> str:
    cleaned = (final_question or "").replace(FORCE_ZENITH_SYMBOL, "").strip()
    return (
        "✨ Estrella ✨\n"
        "Final Reading (template)\n\n"
        "Intention: ...\n"
        "Forward action: ...\n"
        "Past reflection: ...\n"
        "Energy level: ...\n"
        "Aspirational message: ...\n\n"
        f"Session stats: {stats}\n"
        f"Question: {cleaned}"
    )