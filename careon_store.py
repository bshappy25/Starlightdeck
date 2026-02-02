import streamlit as st

def render_store(bank, bank_path):
    """
    Careon Store (mock purchases only)
    - No real payments
    - Adds Careons directly to balance
    """

    st.session_state.setdefault("show_store", False)

    # Style the button to look like the Careon pill
    st.markdown(
        """
        <style>
        .careon-store-wrap .stButton > button {
            display: inline-block;
            width: auto !important;
            padding: 0.42em 0.95em !important;
            border-radius: 999px !important;
            background: rgba(246, 193, 119, 0.14) !important;
            color: #ffd27a !important;
            font-weight: 900 !important;
            letter-spacing: 0.08em !important;
            border: 1px solid rgba(246, 193, 119, 0.38) !important;
            text-shadow: 0 0 12px rgba(246,193,119,0.35) !important;
            box-shadow:
                0 0 12px rgba(246,193,119,0.55),
                0 0 28px rgba(246,193,119,0.25) !important;
            background-color: rgba(246, 193, 119, 0.14) !important;
            margin: 0 auto !important;
        }
        .careon-store-wrap .stButton {
            display:flex;
            justify-content:center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Careon bubble (button)
    st.markdown("<div class='careon-store-wrap'>", unsafe_allow_html=True)
    if st.button("Careon Ȼ", key="open_store_btn"):
        st.session_state["show_store"] = not st.session_state["show_store"]
    st.markdown("</div>", unsafe_allow_html=True)

    # Store panel
    if st.session_state["show_store"]:
        st.markdown("### 🛒 Careon Store (Test)")
        st.caption("No payment integration. Simulated purchases only.")

        c1, c2, c3 = st.columns(3)

        def _mock_buy(dollars: int, tokens: int):
            b = bank.load_bank(bank_path)
            bank.earn(b, tokens, note=f"mock purchase ${dollars} -> +{tokens}Ȼ")
            b.setdefault("history", [])
            b["history"].append({
                "type": "purchase_mock",
                "amount": tokens,
                "note": f"Mock purchase ${dollars}",
                "meta": {"usd": dollars, "tokens": tokens}
            })
            bank.save_bank(b, bank_path)
            st.success(f"Mock purchase complete: +{tokens}Ȼ")
            st.rerun()

        with c1:
            st.markdown("**$1**")
            st.markdown("**+1000Ȼ**")
            if st.button("Buy", key="buy_1"):
                _mock_buy(1, 1000)

        with c2:
            st.markdown("**$5**")
            st.markdown("**+6000Ȼ**")
            if st.button("Buy", key="buy_5"):
                _mock_buy(5, 6000)

        with c3:
            st.markdown("**$10**")
            st.markdown("**+12000Ȼ**")
            if st.button("Buy", key="buy_10"):
                _mock_buy(10, 12000)

        if st.button("Close Store", key="close_store_btn"):
            st.session_state["show_store"] = False
            st.rerun()