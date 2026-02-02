import streamlit as st

def render_store(bank, bank_path: str):
    """
    Careon Store (mock purchases ONLY)
    - Store panel only appears when st.session_state['show_store'] is True
    - No payment integration
    - Adds Careons to balance
    """

    st.session_state.setdefault("show_store", False)

    # Only render when opened by Careon bubble
    if not st.session_state.get("show_store", False):
        return

    # Small panel CSS (top-of-page friendly)
    st.markdown(
        """
        <style>
        .store-panel {
            margin: 0.65rem auto 0.2rem auto;
            max-width: 920px;
            border-radius: 18px;
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.12);
            padding: 14px 16px;
            backdrop-filter: blur(10px);
            box-shadow: 0 14px 30px rgba(0,0,0,0.20);
        }

        .store-title {
            font-size: 1.15rem;
            font-weight: 900;
            letter-spacing: 0.08em;
            color: rgba(245,245,247,0.96);
            margin-bottom: 0.2rem;
        }

        .store-sub {
            color: rgba(245,245,247,0.78);
            font-size: 0.93rem;
            margin-bottom: 0.65rem;
        }

        .store-card {
            border-radius: 16px;
            background: rgba(0,0,0,0.14);
            border: 1px solid rgba(255,255,255,0.10);
            padding: 12px 12px;
        }

        .store-price {
            font-weight: 950;
            font-size: 1.1rem;
            letter-spacing: 0.06em;
            color: #ffd27a;
            text-shadow: 0 0 10px rgba(246,193,119,0.25);
            margin-bottom: 0.15rem;
        }

        .store-tokens {
            font-weight: 900;
            font-size: 1.05rem;
            letter-spacing: 0.06em;
            color: rgba(245,245,247,0.92);
            margin-bottom: 0.5rem;
        }

        .store-note {
            color: rgba(245,245,247,0.72);
            font-size: 0.85rem;
            margin-top: 0.35rem;
        }

        .store-panel .stButton > button {
            border-radius: 14px;
            font-weight: 850;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="store-panel">
            <div class="store-title">🛒 Careon Store</div>
            <div class="store-sub">Test build • No payment integration • Adds tokens instantly</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Layout
    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.9])

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
        st.markdown('<div class="store-card">', unsafe_allow_html=True)
        st.markdown('<div class="store-price">$1</div>', unsafe_allow_html=True)
        st.markdown('<div class="store-tokens">+1000Ȼ</div>', unsafe_allow_html=True)
        if st.button("Buy", key="buy_1"):
            _mock_buy(1, 1000)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="store-card">', unsafe_allow_html=True)
        st.markdown('<div class="store-price">$5</div>', unsafe_allow_html=True)
        st.markdown('<div class="store-tokens">+6000Ȼ</div>', unsafe_allow_html=True)
        if st.button("Buy", key="buy_5"):
            _mock_buy(5, 6000)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="store-card">', unsafe_allow_html=True)
        st.markdown('<div class="store-price">$10</div>', unsafe_allow_html=True)
        st.markdown('<div class="store-tokens">+12000Ȼ</div>', unsafe_allow_html=True)
        if st.button("Buy", key="buy_10"):
            _mock_buy(10, 12000)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        if st.button("Close", key="close_store_btn"):
            st.session_state["show_store"] = False
            st.rerun()

        st.markdown(
            "<div class='store-note'>Tip: Press the gold Careon bubble again to toggle the store.</div>",
            unsafe_allow_html=True
        )