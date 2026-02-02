import streamlit as st
import html

def render_header(ticker_items=None):
    """
    Top-of-page header for Starlight Deck:
    - Subtitle
    - Slow ticker (AVV buffers between phrases)
    - Golden Careon bubble button (toggles store via st.session_state['show_store'])
    """

    st.session_state.setdefault("show_store", False)

    # ---------- CSS (header-only) ----------
    st.markdown(
        """
        <style>
        /* Header tone */
        .sld-top {
            text-align: center;
            margin-top: 0.6rem;
            margin-bottom: 0.35rem;
        }

        .sld-sub {
            color: rgba(245,245,247,0.82);
            font-size: 0.95rem;
            line-height: 1.25rem;
            margin-bottom: 0.55rem;
        }

        /* Soft title */
        .sld-title {
            font-size: 2.2rem;
            font-weight: 900;
            letter-spacing: 0.14em;
            color: #ffd27a;
            text-shadow:
                0 2px 10px rgba(0,0,0,0.55),
                0 0 28px rgba(246,193,119,0.35);
            margin: 0.25rem 0 0.35rem 0;
            user-select: none;
        }

        /* Ticker container */
        .ticker-wrap {
            margin: 0.55rem auto 0.35rem auto;
            padding: 10px 0;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            overflow: hidden;
            position: relative;
            max-width: 900px;
            backdrop-filter: blur(8px);
            box-shadow: 0 10px 24px rgba(0,0,0,0.18);
        }

        .ticker-track {
            display: inline-block;
            white-space: nowrap;
            will-change: transform;
            animation: tickerScroll 88s linear infinite; /* slower + calmer */
            padding-left: 100%;
        }

        @keyframes tickerScroll {
            0%   { transform: translateX(0); }
            100% { transform: translateX(-100%); }
        }

        .ticker-item {
            display: inline-flex;
            align-items: center;
            gap: 14px;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-size: 0.93rem;
            color: rgba(245,245,247,0.92);
        }

        .dot { opacity: 0.55; margin: 0 16px; }

        .acuity  { color: #59a6ff; text-shadow: 0 0 10px rgba(89,166,255,0.25); }
        .valor   { color: #ff5b5b; text-shadow: 0 0 10px rgba(255,91,91,0.20); }
        .variety { color: #ffe27a; text-shadow: 0 0 10px rgba(255,226,122,0.20); }

        /* Careon bubble button styling */
        .careon-btn-wrap .stButton > button {
            width: auto !important;
            padding: 0.48em 1.05em !important;
            border-radius: 999px !important;
            background: rgba(246,193,119,0.14) !important;
            color: #ffd27a !important;
            font-weight: 950 !important;
            letter-spacing: 0.09em !important;
            border: 1px solid rgba(246,193,119,0.42) !important;
            text-shadow: 0 0 12px rgba(246,193,119,0.35) !important;
            box-shadow:
                0 0 14px rgba(246,193,119,0.55),
                0 0 36px rgba(246,193,119,0.22) !important;
            background-color: rgba(246,193,119,0.14) !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .careon-btn-wrap .stButton > button:hover {
            transform: translateY(-1px) scale(1.03);
            box-shadow:
                0 0 18px rgba(246,193,119,0.78),
                0 0 52px rgba(246,193,119,0.32) !important;
        }

        .careon-btn-wrap .stButton {
            display: flex;
            justify-content: center;
        }

        /* Tiny sparkle under header */
        .sld-spark {
            font-size: 0.9rem;
            opacity: 0.7;
            letter-spacing: 0.25em;
            margin-top: 0.1rem;
            margin-bottom: 0.25rem;
            user-select: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------- Title + subtitle ----------
    st.markdown(
        """
        <div class="sld-top">
            <div class="sld-title">✦ STARLIGHT DECK ✦</div>
            <div class="sld-sub">
                A calm, reflective card experience<br/>
                guided by intuition and gentle structure.
            </div>
            <div class="sld-spark">✦ ✧ ✦</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------- Build ticker stream (phrases separated by AVV buffers) ----------
    avv = (
        '<span class="acuity">ACUITY</span><span class="dot">&bull;</span>'
        '<span class="valor">VALOR</span><span class="dot">&bull;</span>'
        '<span class="variety">VARIETY</span>'
    )

    cleaned = []
    if ticker_items:
        for s in ticker_items:
            s = (s or "").strip()
            if s:
                # allow some length so "USER: phrase" shows, but keep it tidy
                cleaned.append(html.escape(s[:42]))

    if not cleaned:
        # Stand-in phrase when none exist yet
        msg = "DONATE TO ADD A PHRASE"
        stream = f"{html.escape(msg)} <span class='dot'>&bull;</span> {avv} <span class='dot'>&bull;</span> {html.escape(msg)}"
    else:
        parts = []
        for msg in cleaned:
            parts.append(msg)
            parts.append(avv)
        stream = (" <span class='dot'>&bull;</span> ".join(parts)) * 2

    st.markdown(
        f"""
        <div class="ticker-wrap">
          <div class="ticker-track">
            <span class="ticker-item">{stream}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------- Careon bubble (the ONLY way to open the store) ----------
    st.markdown("<div class='careon-btn-wrap'>", unsafe_allow_html=True)
    if st.button("Careon Ȼ", key="careon_bubble_btn"):
        st.session_state["show_store"] = not st.session_state.get("show_store", False)
    st.markdown("</div>", unsafe_allow_html=True)