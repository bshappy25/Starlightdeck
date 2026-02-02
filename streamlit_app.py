import random
import streamlit as st

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
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
def rapid_zenith_roll(trials: int = 20, chance: float = 0.05) -> bool:
    """True if at least one Zenith hit occurs across N trials."""
    return any(random.random() < chance for _ in range(trials))

def ensure_state():
    st.session_state.setdefault("mode", None)
    st.session_state.setdefault("balance", 25)          # local demo tokens
    st.session_state.setdefault("network_fund", 0)      # local demo fund
    st.session_state.setdefault("last_result", None)

def spend(cost: int):
    st.session_state["balance"] -= cost
    st.session_state["network_fund"] += cost

def earn(amount: int):
    st.session_state["balance"] += amount

ensure_state()

# ---------- UI ----------
st.title("✦ Starlight Deck ✦")

st.markdown(
    """
    A calm, reflective card experience  
    guided by intuition and gentle structure.
    """
)

st.markdown(
    f"""
    <div style="text-align:center; margin-top:1em;">
        <span class="careon">Careon Ȼ</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Status line (local demo values for now)
st.markdown(
    f"""
    <div class="cardbox">
      <b>Balance:</b> {st.session_state["balance"]} Ȼ &nbsp;&nbsp; • &nbsp;&nbsp;
      <b>🌐 SLD Network Fund:</b> {st.session_state["network_fund"]} Ȼ
    </div>
    """,
    unsafe_allow_html=True,
)

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

# ---------- Normal (stub for now) ----------
if mode == "normal":
    st.info("Normal Mode web port is next. Rapid Mode is live now for testing.")

# ---------- Rapid Mode (LIVE) ----------
if mode == "rapid":
    st.subheader("⚡ Rapid Mode")
    st.write("Cost: **5 Ȼ** • Roll: **20 pulses @ 5%** • Win condition: **≥ 1 Zenith**")
    st.write("Success payout: **+20 Ȼ** + **+3 Ȼ completion** • Failure payout: **+1 Ȼ completion**")

    cols = st.columns(2)
    with cols[0]:
        run = st.button("Run Rapid (-5 Ȼ)")
    with cols[1]:
        reset = st.button("Reset Demo Wallet")

    if reset:
        st.session_state["balance"] = 25
        st.session_state["network_fund"] = 0
        st.session_state["last_result"] = None
        st.rerun()

    if run:
        if st.session_state["balance"] < 5:
            st.error("Not enough Careons to run Rapid Mode.")
        else:
            # Pay entry (funds the network)
            spend(5)

            success = rapid_zenith_roll(trials=20, chance=0.05)

            if success:
                estrella_line = "★ Estrella ★ Bold move, you will be rewarded kindly."
                earn(20)
                earn(3)
                st.session_state["last_result"] = ("SUCCESS", estrella_line)
            else:
                estrella_line = "★ Estrella ★ Recklessness can be costly."
                earn(1)
                st.session_state["last_result"] = ("FAILURE", estrella_line)

            st.rerun()

    # Show last result nicely
    if st.session_state["last_result"]:
        status, estrella_line = st.session_state["last_result"]
        if status == "SUCCESS":
            st.success(status)
        else:
            st.warning(status)

        st.markdown(
            f"""
            <div class="cardbox">
              <div style="font-size:1.15rem;"><b>{estrella_line}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div class="footer">Community-powered • Early test build</div>', unsafe_allow_html=True)