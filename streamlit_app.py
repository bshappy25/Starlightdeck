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
    st.subheader("🃏 Normal Mode")

    # Import here so Streamlit doesn't crash if file is missing during early UI work
    try:
        from SLD_Cleanv2 import draw_card, zenith_check, get_vibe_fields, new_stats
        # Optional: if you added it
        try:
            from SLD_Cleanv2 import display_card_web
        except Exception:
            display_card_web = None
    except Exception as e:
        st.error("SLD_Cleanv2.py is not wired yet (import failed).")
        st.code(str(e))
        st.stop()

    # ----- Init session state for the round -----
    st.session_state.setdefault("normal_draws", [])
    st.session_state.setdefault("normal_stats", new_stats())
    st.session_state.setdefault("normal_paid", False)
    st.session_state.setdefault("normal_message", None)
    st.session_state.setdefault("normal_done", False)

    # Load bank
    b = bank.load_bank(BANK_PATH)

    # Charge once per round
    if not st.session_state["normal_paid"]:
        if b.get("balance", 0) < 1:
            st.error("Not enough Careons to start a Normal round (-1 Ȼ).")
        else:
            if bank.spend(b, 1, note="normal round start"):
                bank.save_bank(b, BANK_PATH)
                st.session_state["normal_paid"] = True
                st.session_state["normal_message"] = "Round started (-1 Ȼ)."
                st.rerun()
            else:
                st.error("Not enough Careons to start a Normal round (-1 Ȼ).")

    # Controls
    c1, c2, c3 = st.columns(3)
    draw_pressed = c1.button("Draw Next Card")
    finish_pressed = c2.button("Finish (Final)")
    reset_pressed = c3.button("Reset Round")

    if reset_pressed:
        st.session_state["normal_draws"] = []
        st.session_state["normal_stats"] = new_stats()
        st.session_state["normal_paid"] = False
        st.session_state["normal_message"] = "Round reset."
        st.session_state["normal_done"] = False
        st.rerun()

    stats = st.session_state["normal_stats"]

    # Draw action
    if draw_pressed and not st.session_state["normal_done"]:
        if stats["draws"] >= 20:
            st.session_state["normal_done"] = True
            st.session_state["normal_message"] = "20 cards reached. Press Finish (Final)."
            st.rerun()

        vibe, level = draw_card()
        stats["draws"] += 1
        stats["vibe"][vibe] += 1
        stats["level"][level] += 1

        # For Streamlit, we aren't doing the "ask optional question" gate yet.
        # Forced zenith can be added later via a checkbox.
        zenith, _forced_flag = zenith_check(False)

        if zenith:
            stats["zenith"] += 1

        fields = get_vibe_fields(vibe, level, zenith)

        st.session_state["normal_draws"].append({
            "vibe": vibe,
            "level": level,
            "zenith": zenith,
            "fields": fields,
        })

        # Estrella checkpoints: award +1 at 10 and +1 at 20 (once-per-round)
        if stats["draws"] == 10:
            b = bank.load_bank(BANK_PATH)
            bank.award_once_per_round(b, note="estrella-10", amount=1)
            bank.save_bank(b, BANK_PATH)
            st.session_state["normal_message"] = "★ Estrella ★ 10-card insight (+1 Ȼ)."
        elif stats["draws"] == 20:
            b = bank.load_bank(BANK_PATH)
            bank.award_once_per_round(b, note="estrella-20", amount=1)
            bank.save_bank(b, BANK_PATH)
            st.session_state["normal_done"] = True
            st.session_state["normal_message"] = "★ Estrella ★ 20-card ratio insight (+1 Ȼ). Press Finish (Final)."
        else:
            st.session_state["normal_message"] = None

        st.session_state["normal_stats"] = stats
        st.rerun()

    # Finish action (completion bonus)
    if finish_pressed and st.session_state["normal_done"]:
        b = bank.load_bank(BANK_PATH)
        bank.award_once_per_round(b, note="estrella-final", amount=1)
        bonus = bank.award_once_per_round(b, note="completion-bonus", amount=3)
        bank.save_bank(b, BANK_PATH)

        if bonus:
            st.session_state["normal_message"] = "🎉 COMPLETION BONUS: +3 Ȼ (three tasks complete)."
        else:
            st.session_state["normal_message"] = "★ Estrella ★ Session complete."
        st.rerun()

    # Status
    st.write(f"Draws: **{stats['draws']} / 20**")
    if st.session_state["normal_message"]:
        st.markdown(
            f"<div class='cardbox'><b>{st.session_state['normal_message']}</b></div>",
            unsafe_allow_html=True
        )

    # Render cards
    if st.session_state["normal_draws"]:
        for i, d in enumerate(st.session_state["normal_draws"], start=1):
            if display_card_web:
                txt = display_card_web(i, d["vibe"], d["level"], d["zenith"], d["fields"], stats)
            else:
                # fallback text if you haven't added display_card_web yet
                z = "◇ ZENITH ◇" if d["zenith"] else ""
                txt = (
                    f"Card #{i}\n"
                    f"{d['vibe'].upper()} | Level {d['level']} {z}\n"
                    + "\n".join([f"{k}: {v}" for k, v in d["fields"].items()])
                )
            st.markdown(f"<div class='cardbox'><pre>{txt}</pre></div>", unsafe_allow_html=True)
    else:
        st.caption("Draw your first card to begin.")

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
