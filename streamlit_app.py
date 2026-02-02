import os
import random
import streamlit as st

import careon_bank_v2 as bank

# ---------- Paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "careon_bank_v2.json")

# ---------- Page config ----------
st.set_page_config(page_title="Starlight Deck", layout="centered")

# ---------- Style ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f1021 0%, #1b1d3a 100%);
        color: #f5f5f7;
    }
    h1 { color: #f6c177; text-align: center; letter-spacing: 0.05em; }
    p, li, span, div { color: #e6e6eb; font-size: 1.05rem; }
    .stButton > button {
        background-color: #3f44c8; color: white; border-radius: 12px;
        padding: 0.6em 1.2em; border: none; font-size: 1.05rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { background-color: #5a5ff0; transform: scale(1.03); }
    .careon {
        display: inline-block; padding: 0.35em 0.75em; border-radius: 999px;
        background: rgba(246, 193, 119, 0.15); color: #f6c177;
        font-weight: 600; letter-spacing: 0.04em;
    }
    .cardbox {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 14px 16px;
        margin-top: 12px;
    }
    .footer { text-align: center; opacity: 0.75; font-size: 0.85rem; margin-top: 2em; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Helpers ----------
def rapid_zenith_roll(trials: int = 20, chance: float = 0.05) -> bool:
    return any(random.random() < chance for _ in range(trials))

def reset_bank_file():
    b0 = {"balance": 25, "sld_network_fund": 0, "history": []}
    bank.save_bank(b0, BANK_PATH)

# ---------- Session state ----------
st.session_state.setdefault("mode", None)
st.session_state.setdefault("last_result", None)

# ---------- Load persistent bank ----------
b = bank.load_bank(BANK_PATH)

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

# Status box (HTML kept single-line to avoid f-string argument issues)
status_html = (
    f'<div class="cardbox">'
    f'<b>Balance:</b> {b.get("balance", 0)} Ȼ &nbsp;&nbsp; • &nbsp;&nbsp; '
    f'<b>🌐 SLD Network Fund:</b> {b.get("sld_network_fund", 0)} Ȼ'
    f'</div>'
)
st.markdown(status_html, unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("Start Normal"):
        st.session_state["mode"] = "normal"
        st.session_state["last_result"] = None
with col2:
    if st.button("Start Rapid"):
        st.session_state["mode"] = "rapid"
        st.session_state["last_result"] = None

mode = st.session_state.get("mode")

if mode == "normal":
    st.info("Normal Mode web port is next. Rapid Mode is live now for testing.")

if mode == "rapid":
    st.subheader("⚡ Rapid Mode")
    st.write("Cost: **5 Ȼ** • Roll: **20 pulses @ 5%** • Win condition: **≥ 1 Zenith**")
    st.write("Success payout: **+20 Ȼ** + **+3 Ȼ completion** • Failure payout: **+1 Ȼ completion**")

    cA, cB = st.columns(2)
    run = cA.button("Run Rapid (-5 Ȼ)")
    reset = cB.button("Reset Wallet")

    if reset:
        reset_bank_file()
        st.session_state["last_result"] = None
        st.rerun()

    if run:
        b = bank.load_bank(BANK_PATH)

        if b.get("balance", 0) < 5:
            st.error("Not enough Careons to run Rapid Mode.")
        else:
            # ALL spend funds the network
            if not bank.spend(b, 5, note="rapid charge"):
                st.error("Not enough Careons to run Rapid Mode.")
            else:
                success = rapid_zenith_roll(trials=20, chance=0.05)

                if success:
                    estrella_line = "★ Estrella ★ Bold move, you will be rewarded kindly."
                    bank.award_once_per_round(b, note="rapid-success-20", amount=20)
                    bank.award_once_per_round(b, note="rapid-completion-bonus", amount=3)
                    st.session_state["last_result"] = ("SUCCESS", estrella_line)
                else:
                    estrella_line = "★ Estrella ★ Recklessness can be costly."
                    bank.award_once_per_round(b, note="rapid-fail-completion", amount=1)
                    st.session_state["last_result"] = ("FAILURE", estrella_line)

                bank.save_bank(b, BANK_PATH)
                st.rerun()

    if st.session_state["last_result"]:
        status, estrella_line = st.session_state["last_result"]
        if status == "SUCCESS":
            st.success(status)
        else:
            st.warning(status)

        result_html = f'<div class="cardbox"><div style="font-size:1.15rem;"><b>{estrella_line}</b></div></div>'
        st.markdown(result_html, unsafe_allow_html=True)

st.markdown('<div class="footer">Community-powered • Early test build</div>', unsafe_allow_html=True)
