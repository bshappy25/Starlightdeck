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
)

# ---------- Helpers ----------
def deposit_into_bank(amount: int, note: str) -> None:
    """
    Deposit policy (simple + community aligned):
    - Adds amount to user balance
    - Adds amount to SLD network fund
    - Adds history line
    """
    b = bank.load_bank(BANK_PATH)
    b["balance"] = int(b.get("balance", 0)) + int(amount)
    b["sld_network_fund"] = int(b.get("sld_network_fund", 0)) + int(amount)
    b.setdefault("history", [])
    b["history"].append(note)
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
st.title("✦ Starlight Deck ✦")

st.markdown(
    """
    A calm, reflective card experience  
    guided by intuition and gentle structure.
    """
)

st.markdown(
    '<div style="text-align:center; margin-top:1em;"><span class="careon">Careon Ȼ</span></div>',
    unsafe_allow_html=True
)

# Status box
b = bank.load_bank(BANK_PATH)
status_html = (
    f'<div class="cardbox">'
    f'<b>Balance:</b> {b.get("balance", 0)} Ȼ &nbsp;&nbsp; • &nbsp;&nbsp; '
    f'<b>🌐 SLD Network Fund:</b> {b.get("sld_network_fund", 0)} Ȼ'
    f'</div>'
)
st.markdown(status_html, unsafe_allow_html=True)

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