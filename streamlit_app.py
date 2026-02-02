import os
import random
import streamlit as st

import codes_ledger

import careon_bank_v2 as bank

# ---------- Paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "careon_bank_v2.json")
LEDGER_PATH = os.path.join(HERE, "codes_ledger.json")
# ---------- Page config ----------
st.set_page_config(page_title="Starlight Deck", layout="centered")

# ---------- Style ----------
st.markdown("### Deposit Codes")

redeem_code = st.text_input("Redeem code", placeholder="DEP-50-XXXXXX", key="redeem_code_input")
if st.button("Redeem", key="redeem_btn"):
    ok, msg, amt = codes_ledger.redeem_code(LEDGER_PATH, redeem_code, redeemer="web")
    if ok:
        deposit_into_bank(amt, f"Deposit redeemed: +{amt} Ȼ (code)")
        st.success(f"{msg} +{amt} Ȼ added.")
        st.rerun()
    else:
        st.error(msg)

st.markdown("---")

st.markdown(
    "<div class='muted'>Admin: <b>bshapp</b></div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        text-align:center;
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: 0.12em;
        color: #ffd27a;
        text-shadow:
            0 2px 8px rgba(0,0,0,0.6),
            0 0 22px rgba(246,193,119,0.55),
            0 0 48px rgba(246,193,119,0.25);
        margin-top: 0.4em;
    ">
        ✦ STARLIGHT DECK ✦
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("### Admin")

# Admin login (password checked against secrets/env)
admin_pw = st.text_input("Admin password", type="password", key="admin_pw_input")
if st.button("Unlock Admin", key="admin_unlock_btn"):
    secret_pw = None
    try:
        secret_pw = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        secret_pw = None
    if not secret_pw:
        secret_pw = os.getenv("SLD_ADMIN_PASSWORD")

    if secret_pw and admin_pw == secret_pw:
        st.session_state["admin_ok"] = True
        st.success("Admin unlocked.")
        st.rerun()
    else:
        st.session_state["admin_ok"] = False
        st.error("Wrong password.")

if st.session_state.get("admin_ok"):
    st.markdown("#### Generate deposit code")
    amt = st.selectbox("Amount", [25, 50, 100, 250], index=1, key="gen_amt")
    if st.button("Generate Code", key="gen_code_btn"):
        new_code = codes_ledger.add_code(LEDGER_PATH, int(amt))
        st.code(new_code)
        st.info("Give this code to a user. It can be redeemed once.")

    st.markdown("#### Devtool (Admin only)")
    dev = st.text_input("Devtool code", placeholder="TGIF", key="admin_devtool_input")
    if st.button("Apply Devtool", key="admin_devtool_apply"):
        if (dev or "").strip().upper() == "TGIF":
            # TGIF adds +5 to balance (and optionally network fund — you choose)
            # I recommend: balance only (dev/test), NOT network fund.
            b2 = bank.load_bank(BANK_PATH)
            b2["balance"] = int(b2.get("balance", 0)) + 5
            b2.setdefault("history", [])
            b2["history"].append("TGIF (admin): +5 Ȼ")
            bank.save_bank(b2, BANK_PATH)
            st.success("TGIF applied: +5 Ȼ")
            st.rerun()
        else:
            st.error("Unknown devtool code.")

# ---------- Admin: Community Reward ----------
b = bank.load_bank(BANK_PATH)
if b.get("sld_network_fund", 0) >= 1000:
    st.markdown("#### 🎁 Community Reward")

    if st.button("Generate 20Ȼ Reward Code", key="gen_reward_code"):
        reward_code = codes_ledger.add_code(LEDGER_PATH, 20)
        st.code(reward_code)
        st.info("Reward code generated. Share intentionally.")
else:
    st.markdown(
        "<div class='muted'>Community reward unlocks at 1000 Ȼ.</div>",
        unsafe_allow_html=True
    )

# ---------- Helpers ----------
def deposit_into_bank(amount: int, note: str) -> None:
    """
    Deposit policy:
    - 95% goes to user balance
    - 5% goes to SLD Network Fund
    """
    amount = int(amount)
    if amount <= 0:
        return

    network_cut = amount // 20        # 5%
    user_amount = amount - network_cut

    b = bank.load_bank(BANK_PATH)

    b["balance"] = int(b.get("balance", 0)) + user_amount
    b["sld_network_fund"] = int(b.get("sld_network_fund", 0)) + network_cut

    b.setdefault("history", [])
    b["history"].append(
        f"Deposit redeemed: +{user_amount} Ȼ (network +{network_cut} Ȼ)"
    )

    bank.save_bank(b, BANK_PATH)


def is_admin() -> bool:
    """
    Admin gate:
    - Uses Streamlit secrets if present: st.secrets["ADMIN_PASSWORD"]
    - Else uses env var: SLD_ADMIN_PASSWORD
    """
    pw = None
    try:
        pw = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        pw = None
    if not pw:
        pw = os.getenv("SLD_ADMIN_PASSWORD")
    if not pw:
        return False
    return st.session_state.get("admin_ok", False)

def rapid_zenith_roll(trials: int = 20, chance: float = 0.05) -> bool:
    return any(random.random() < chance for _ in range(trials))

def ensure_bank_exists():
    """
    If the bank file doesn't exist or is corrupted, reset it safely.
    """
    try:
        _ = bank.load_bank(BANK_PATH)
    except Exception:
        b0 = {"balance": 25, "sld_network_fund": 0, "history": []}
        bank.save_bank(b0, BANK_PATH)

def reset_bank_file():
    b0 = {"balance": 25, "sld_network_fund": 0, "history": []}
    bank.save_bank(b0, BANK_PATH)

def push_history_line(b: dict, line: str, keep: int = 12) -> None:
    b.setdefault("history", [])
    b["history"].append(line)
    if len(b["history"]) > keep:
        b["history"] = b["history"][-keep:]

# ---------- Init ----------
ensure_bank_exists()

# ---------- Session state ----------
st.session_state.setdefault("last_result", None)   # ("SUCCESS"/"FAILURE", estrella_line)
st.session_state.setdefault("last_roll", None)     # bool success
st.session_state.setdefault("devtool_msg", None)

# ---------- Load persistent bank ----------
b = bank.load_bank(BANK_PATH)

# ---------- Sidebar (controls + TGIF devtool) ----------
with st.sidebar:
    st.markdown("### Controls")

    # Reset wallet
    if st.button("Reset Wallet (25 Ȼ)", key="sb_reset_wallet"):
        reset_bank_file()
        st.session_state["last_result"] = None
        st.session_state["last_roll"] = None
        st.session_state["devtool_msg"] = "Wallet reset to 25 Ȼ."
        st.rerun()

    st.markdown("---")

    st.markdown("### Devtool")
    st.markdown("<div class='muted'>Enter <b>TGIF</b> to add <b>+5 Ȼ</b>.</div>", unsafe_allow_html=True)

    dev_input = st.text_input("Devtool code", value="", placeholder="TGIF", key="devtool_input")
    if st.button("Apply Devtool", key="sb_apply_devtool"):
        code = (dev_input or "").strip().upper()
        b2 = bank.load_bank(BANK_PATH)

        if code == "TGIF":
            # Award +5 and log it
            bank.award_once_per_round(b2, note="devtool-tgif", amount=5)
            push_history_line(b2, "TGIF applied: +5 Ȼ")
            bank.save_bank(b2, BANK_PATH)
            st.session_state["devtool_msg"] = "✅ TGIF applied: +5 Ȼ"
            st.rerun()
        else:
            st.session_state["devtool_msg"] = "❌ Unknown code."
            st.rerun()

    if st.session_state.get("devtool_msg"):
        st.info(st.session_state["devtool_msg"])

    st.markdown("---")
    st.markdown("### About")
    st.markdown("<div class='muted'>Community-powered • Early test build</div>", unsafe_allow_html=True)

# ---------- UI ----------
# ---------- Style (Refreshed UI) ----------
st.markdown(
    r"""
    <style>
    :root {
        --bg1: #120A2A;   /* deep purple */
        --bg2: #1A0F3D;
        --panel: rgba(255,255,255,0.06);
        --panelBorder: rgba(255,255,255,0.10);
        --gold: #f6c177;
        --gold2: #ffd27a;
        --text: #f5f5f7;
        --muted: rgba(245,245,247,0.82);
        --btn: #3f44c8;
        --btnHover: #5a5ff0;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 50% -10%, rgba(255, 210, 122, 0.12), transparent 60%),
                    linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
        color: var(--text);
    }

    h1 { color: var(--gold); text-align: center; letter-spacing: 0.06em; }
    p, li, span, div { color: var(--text); font-size: 1.05rem; }
    .muted { color: var(--muted); font-size: 0.95rem; }

    .cardbox {
        background: var(--panel);
        border: 1px solid var(--panelBorder);
        border-radius: 16px;
        padding: 14px 16px;
        margin-top: 12px;
        box-shadow: 0 0 0 rgba(0,0,0,0);
    }

    .stButton > button {
        background-color: var(--btn);
        color: white;
        border-radius: 14px;
        padding: 0.65em 1.2em;
        border: none;
        font-size: 1.05rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover { background-color: var(--btnHover); transform: scale(1.01); }

    /* Careon pill */
    .careon-pill-wrap { text-align:center; margin-top: 1.1em; margin-bottom: 0.6em; }

    .careon-pill {
        display: inline-block;
        padding: 0.42em 0.95em;
        border-radius: 999px;
        background: rgba(246, 193, 119, 0.14);
        color: var(--gold2);
        font-weight: 800;
        letter-spacing: 0.08em;
        border: 1px solid rgba(246, 193, 119, 0.38);
        text-shadow: 0 0 12px rgba(246,193,119,0.35);
        box-shadow:
            0 0 12px rgba(246,193,119,0.55),
            0 0 28px rgba(246,193,119,0.25);
        animation: careonPulse 2.6s ease-in-out infinite;
        user-select: none;
    }

    @keyframes careonPulse {
        0% {
            transform: translateY(0px);
            box-shadow:
                0 0 12px rgba(246,193,119,0.45),
                0 0 28px rgba(246,193,119,0.20);
        }
        50% {
            transform: translateY(-1px);
            box-shadow:
                0 0 18px rgba(246,193,119,0.78),
                0 0 44px rgba(246,193,119,0.33);
        }
        100% {
            transform: translateY(0px);
            box-shadow:
                0 0 12px rgba(246,193,119,0.45),
                0 0 28px rgba(246,193,119,0.20);
        }
    }

    .footer { text-align: center; opacity: 0.75; font-size: 0.85rem; margin-top: 2em; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- UI Header ----------

# ---------- UI Header ----------

# Pop title (stronger than st.title)
st.markdown(
    """
    
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<div class='muted' style='text-align:center; margin-bottom: 0.6em;'>"
    "A calm, reflective card experience<br/>guided by intuition and gentle structure."
    "</div>",
    unsafe_allow_html=True
)

# Clickable Careon pill (placeholder purchase link)
st.markdown(
    """
    <div class='careon-pill-wrap'>
        <a href="#"
           class="careon-pill"
           style="text-decoration:none;"
           title="Purchase Careons (coming soon)">
            Careon Ȼ
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# Status box

# ---------- Soft Goal ----------
b = bank.load_bank(BANK_PATH)
goal = 1000
current = int(b.get("sld_network_fund", 0))
progress_pct = min(100, int((current / goal) * 100))

st.markdown(
    f"""
    <div class="cardbox" style="text-align:center;">
        <b>Community Goal:</b> {current} / {goal} Ȼ<br/>
        <div class="muted" style="margin-top:0.3em;">
            When the network reaches {goal} Ȼ, a reward code may be released.
        </div>
        <div style="
            margin-top:0.6em;
            height:10px;
            background: rgba(255,255,255,0.08);
            border-radius: 999px;
            overflow:hidden;
        ">
            <div style="
                width:{progress_pct}%;
                height:100%;
                background: linear-gradient(90deg, #f6c177, #ffd27a);
                box-shadow: 0 0 12px rgba(246,193,119,0.6);
            "></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

b = bank.load_bank(BANK_PATH)
st.markdown(
    f"""
    <div class="cardbox" style="text-align:center;">
        <b>Balance:</b> {b.get("balance", 0)} Ȼ &nbsp;&nbsp; • &nbsp;&nbsp;
        <b>🌐 SLD Network Fund:</b> {b.get("sld_network_fund", 0)} Ȼ
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ---------- Rapid Mode (primary product for now) ----------
st.subheader("⚡ Rapid Mode")

st.write("Cost: **5 Ȼ** • Roll: **20 pulses @ 5%** • Win condition: **≥ 1 Zenith**")
st.write("Success payout: **+20 Ȼ** + **+3 Ȼ completion** • Failure payout: **+1 Ȼ completion**")

cA, cB = st.columns(2)
run = cA.button("Run Rapid (-5 Ȼ)", key="rapid_run")
clear = cB.button("Clear Result", key="rapid_clear_result")

if clear:
    st.session_state["last_result"] = None
    st.session_state["last_roll"] = None
    st.rerun()

if run:
    b = bank.load_bank(BANK_PATH)

    if b.get("balance", 0) < 5:
        st.error("Not enough Careons to run Rapid Mode.")
    else:
        # ALL spend funds the network (handled in bank.spend if implemented that way)
        if not bank.spend(b, 5, note="rapid charge"):
            st.error("Not enough Careons to run Rapid Mode.")
        else:
            success = rapid_zenith_roll(trials=20, chance=0.05)
            st.session_state["last_roll"] = success

            if success:
                estrella_line = "★ Estrella ★ Bold move, you will be rewarded kindly."
                bank.award_once_per_round(b, note="rapid-success-20", amount=20)
                bank.award_once_per_round(b, note="rapid-completion-bonus", amount=3)
                st.session_state["last_result"] = ("SUCCESS", estrella_line)
                push_history_line(b, "Rapid SUCCESS: +20 Ȼ +3 Ȼ")
            else:
                estrella_line = "★ Estrella ★ Recklessness can be costly."
                bank.award_once_per_round(b, note="rapid-fail-completion", amount=1)
                st.session_state["last_result"] = ("FAILURE", estrella_line)
                push_history_line(b, "Rapid FAILURE: +1 Ȼ")

            bank.save_bank(b, BANK_PATH)
            st.rerun()

# ---------- Result display ----------
if st.session_state["last_result"]:
    status, estrella_line = st.session_state["last_result"]

    if status == "SUCCESS":
        st.success(status)
    else:
        st.warning(status)

    result_html = f'<div class="cardbox"><div style="font-size:1.15rem;"><b>{estrella_line}</b></div></div>'
    st.markdown(result_html, unsafe_allow_html=True)

    # Optional detail line
    if st.session_state.get("last_roll") is not None:
        roll_text = "Zenith appeared ✅" if st.session_state["last_roll"] else "No Zenith ❌"
        st.markdown(f"<div class='cardbox'><b>Roll:</b> {roll_text}</div>", unsafe_allow_html=True)

st.divider()

# ---------- Recent history ----------
b = bank.load_bank(BANK_PATH)
hist = b.get("history", []) or []
st.markdown("<div class='cardbox'><b>Recent Activity</b></div>", unsafe_allow_html=True)

if hist:
    # Show newest first
    for line in reversed(hist[-12:]):
        st.markdown(f"<div class='cardbox'>{line}</div>", unsafe_allow_html=True)
else:
    st.caption("No activity yet. Run Rapid Mode to begin.")

st.markdown('<div class="footer">Community-powered • Early test build</div>', unsafe_allow_html=True)