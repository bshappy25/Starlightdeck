import streamlit as st

def render_bubble():
    st.session_state.setdefault("show_market", False)

    # CSS for sleek bubble
    st.markdown(
        """
        <style>
        .careon-bubble-row {
            display: flex;
            justify-content: center;
            margin-top: 0.25rem;
            margin-bottom: 0.55rem;
        }

        .careon-bubble-row .stButton > button {
            width: auto !important;
            padding: 0.56em 1.12em !important;
            border-radius: 999px !important;

            background: linear-gradient(90deg,
              rgba(180,130,255,0.18),
              rgba(120,220,210,0.14)
            ) !important;

            color: #ffd27a !important;
            font-weight: 950 !important;
            letter-spacing: 0.10em !important;

            border: 1px solid rgba(246,193,119,0.42) !important;
            text-shadow: 0 0 12px rgba(246,193,119,0.35) !important;

            box-shadow:
                0 0 18px rgba(246,193,119,0.55),
                0 0 58px rgba(120,220,210,0.12) !important;

            transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease;
        }

        .careon-bubble-row .stButton > button:hover {
            transform: translateY(-1px) scale(1.03);
            filter: brightness(1.05);
            box-shadow:
                0 0 22px rgba(246,193,119,0.78),
                0 0 76px rgba(180,130,255,0.16) !important;
        }

        .careon-bubble-row .stButton { width: auto !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    label = "Careon Ȼ" + (" ✦" if st.session_state.get("show_market") else "")

    st.markdown("<div class='careon-bubble-row'>", unsafe_allow_html=True)
    if st.button(label, key="__sld__careon_market_toggle_btn"):
        st.session_state["show_market"] = not st.session_state.get("show_market", False)
    st.markdown("</div>", unsafe_allow_html=True)