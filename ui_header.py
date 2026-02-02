import streamlit as st

def inject_css():
    """Inject shared header + ticker CSS"""
    st.markdown(
        r"""
        <style>
        /* ---------- Header helpers ---------- */
        .muted { 
            color: rgba(245,245,247,0.82); 
            font-size: 0.95rem; 
        }

        /* ---------- Careon pill ---------- */
        .careon-pill-wrap { 
            text-align:center; 
            margin-top: 0.9em; 
            margin-bottom: 0.6em; 
        }

        .careon-pill {
            display: inline-block;
            padding: 0.42em 0.95em;
            border-radius: 999px;
            background: rgba(246, 193, 119, 0.14);
            color: #ffd27a;
            font-weight: 900;
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
            0%   { transform: translateY(0px); }
            50%  { transform: translateY(-1px); }
            100% { transform: translateY(0px); }
        }

        /* ---------- Ticker ---------- */
        .ticker-wrap {
            margin: 0.7em auto 0.2em auto;
            padding: 10px 0;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.10);
            overflow: hidden;
            position: relative;
            max-width: 860px;
            backdrop-filter: blur(6px);
        }

        .ticker-track {
            display: inline-block;
            white-space: nowrap;
            will-change: transform;
            animation: tickerScroll 22s linear infinite;
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
            letter-spacing: 0.14em;
            text-transform: uppercase;
            font-size: 0.95rem;
        }

        .dot { opacity: 0.55; margin: 0 16px; }

        .acuity  { color: #59a6ff; }
        .valor   { color: #ff5b5b; }
        .variety { color: #ffe27a; }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    """Render the Starlight Deck header + ticker"""
    st.markdown(
        "<div class='muted' style='text-align:center; margin-bottom: 0.45em;'>"
        "A calm, reflective card experience<br/>guided by intuition and gentle structure."
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="ticker-wrap">
          <div class="ticker-track">
            <span class="ticker-item">
              <span class="acuity">ACUITY</span><span class="dot">&bull;</span>
              <span class="valor">VALOR</span><span class="dot">&bull;</span>
              <span class="variety">VARIETY</span><span class="dot">&bull;</span>
              <span class="acuity">ACUITY</span><span class="dot">&bull;</span>
              <span class="valor">VALOR</span><span class="dot">&bull;</span>
              <span class="variety">VARIETY</span>
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='careon-pill-wrap'>
            <span class="careon-pill" title="Careon currency (test build)">
                Careon Ȼ
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )