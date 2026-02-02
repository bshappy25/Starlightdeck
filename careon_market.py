import streamlit as st

def render_market(bank, bank_path: str):
    """
    Careon Market (mock purchases only)
    Appears ONLY when show_market is True.
    Packages:
      $1  -> +1000Ȼ
      $5  -> +6000Ȼ
      $10 -> +12000Ȼ
    """

    st.session_state.setdefault("show_market", False)
    if not st.session_state.get("show_market", False):
        return

    st.markdown(
        """
        <style>
        .market-panel {
            margin: 0.25rem auto 0.8rem auto;
            max-width: 980px;
            border-radius: 20px;
            background: rgba(255,255,255,0.075);
            border: 1px solid rgba(255,255,255,0.14);
            padding: 16px 16px;
            backdrop-filter: blur(12px);
            box-shadow: 0 16px 40px rgba(0,0,0,0.22);
        }

        .market-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 0.75rem;
        }

        .market-title {
            font-size: 1.15rem;
            font-weight: 950;
            letter-spacing: 0.10em;
            color: rgba(245,245,247,0.95);
        }

        .market-sub {
            color: rgba(245,245,247,0.74);
            font-size: 0.92rem;
            margin-top: 0.15rem;
        }

        .market-card {
            border-radius: 18px;
            background: rgba(0,0,0,0.16);
            border: 1px solid rgba(255,255,255,0.12);
            padding: 14px 14px;
        }

        .m-price {
            color: #ffd27a;
            font-weight: 950;
            font-size: 1.05rem;
            letter-spacing: 0.10em;
            text-shadow: 0 0 12px rgba(246,193,119,0.25);
            margin-bottom: 0.2rem;
        }

        .m-tokens {
            color: rgba(245,245,247,0.92);
            font-weight: 900;
            font-size: 1.1rem;
            letter-spacing: 0.06em;
            margin-bottom: 0.55rem;
        }

        .m-note {
            color: rgba(245,245,247,0.70);
            font-size: 0.84rem;
            margin-top: 0.5rem;
        }

        .market-panel .stButton > button {
            border-radius: 14px;
            font-weight: 900;
            letter-spacing: 0.05em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="market-panel">
          <div class="market-head">
            <div>
              <div class="market-title">CAREON MARKET</div>
              <div class="market-sub">Test build • No payment integration • Instant token credit</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.85])

    def _mock_buy(usd: int, tokens: int):
        b = bank.load_bank(bank_path)
        bank.earn(b, tokens, note=f"mock market ${usd} -> +{tokens}Ȼ")
        b.setdefault("history", [])
        b["history"].append({
            "type": "purchase_mock",
            "amount": tokens,
            "note": f"Mock market purchase ${usd}",
            "meta": {"usd": usd, "tokens": tokens}
        })
        bank.save_bank(b, bank_path)
        st.success(f"Market credit complete: +{tokens}Ȼ")
        st.rerun()

    with c1:
        st.markdown("<div class='market-card'>", unsafe_allow_html=True)
        st.markdown("<div class='m-price'>$1</div>", unsafe_allow_html=True)
        st.markdown("<div class='m-tokens'>+1000Ȼ</div>", unsafe_allow_html=True)
        if st.button("Buy", key="m_buy_1"):
            _mock_buy(1, 1000)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='market-card'>", unsafe_allow_html=True)
        st.markdown("<div class='m-price'>$5</div>", unsafe_allow_html=True)
        st.markdown("<div class='m-tokens'>+6000Ȼ</div>", unsafe_allow_html=True)
        if st.button("Buy", key="m_buy_5"):
            _mock_buy(5, 6000)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='market-card'>", unsafe_allow_html=True)
        st.markdown("<div class='m-price'>$10</div>", unsafe_allow_html=True)
        st.markdown("<div class='m-tokens'>+12000Ȼ</div>", unsafe_allow_html=True)
        if st.button("Buy", key="m_buy_10"):
            _mock_buy(10, 12000)
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        if st.button("Close", key="market_close_btn"):
            st.session_state["show_market"] = False
            st.rerun()

        st.markdown("<div class='m-note'>Tip: Press the bubble again to toggle.</div>", unsafe_allow_html=True)