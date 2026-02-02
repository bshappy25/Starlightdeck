import streamlit as st
import html

# -----------------------------------------
# UI HEADER (single banner / single ticker)
# -----------------------------------------

def inject_css(ticker_speed_s: int = 60):
    """
    ticker_speed_s: seconds for one full scroll (bigger = slower).
    """
    st.markdown(
        rf"""
        <style>
        /* ---------- Header helpers ---------- */
        .muted {{
            color: rgba(245,245,247,0.82);
            font-size: 0.95rem;
        }}

        /* ---------- Careon pill ---------- */
        .careon-pill-wrap {{
            text-align:center;
            margin-top: 0.9em;
            margin-bottom: 0.6em;
        }}

        .careon-pill {{
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
        }}

        @keyframes careonPulse {{
            0%   {{ transform: translateY(0px); }}
            50%  {{ transform: translateY(-1px); }}
            100% {{ transform: translateY(0px); }}
        }}

        /* ---------- Ticker (single banner) ---------- */
        .ticker-wrap {{
            margin: 0.7em auto 0.2em auto;
            padding: 10px 0;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.10);
            overflow: hidden;
            position: relative;
            max-width: 860px;
            backdrop-filter: blur(6px);
        }}

        .ticker-track {{
            display: inline-block;
            white-space: nowrap;
            will-change: transform;
            animation: tickerScroll {int(ticker_speed_s)}s linear infinite; /* slower = calmer */
            padding-left: 100%;
        }}

        @keyframes tickerScroll {{
            0%   {{ transform: translateX(0); }}
            100% {{ transform: translateX(-100%); }}
        }}

        .ticker-item {{
            display: inline-flex;
            align-items: center;
            gap: 14px;
            font-weight: 900;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            font-size: 0.95rem;
            color: rgba(245,245,247,0.92);
        }}

        .dot {{ opacity: 0.55; margin: 0 16px; }}

        /* Optional colored words if you keep default */
        .acuity  {{ color: #59a6ff; }}
        .valor   {{ color: #ff5b5b; }}
        .variety {{ color: #ffe27a; }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header(ticker_items=None):
    """
    Renders:
      - subtitle
      - ONE ticker banner (same one)
      - careon pill

    ticker_items:
      - None (default) -> shows ACUITY / VALOR / VARIETY (colored)
      - list[str] -> shows your phrases (plain text, escaped, trimmed to 20 chars)
    """

    st.markdown(
        "<div class='muted' style='text-align:center; margin-bottom: 0.45em;'>"
        "A calm, reflective card experience<br/>guided by intuition and gentle structure."
        "</div>",
        unsafe_allow_html=True
    )

    # Default ticker content (colored)
    if not ticker_items:
        ticker_html = """
            <span class="acuity">ACUITY</span><span class="dot">&bull;</span>
            <span class="valor">VALOR</span><span class="dot">&bull;</span>
            <span class="variety">VARIETY</span><span class="dot">&bull;</span>
            <span class="acuity">ACUITY</span><span class="dot">&bull;</span>
            <span class="valor">VALOR</span><span class="dot">&bull;</span>
            <span class="variety">VARIETY</span>
        """
    else:
        # User phrases (trim to 20, escape HTML, repeat for flow)
        cleaned = []
        for s in ticker_items:
            s = (s or "").strip()
            if not s:
                continue
            cleaned.append(html.escape(s[:20]))
        if not cleaned:
            cleaned = ["WELCOME", "BE KIND", "STAY GOLD"]

        joined = " <span class='dot'>&bull;</span> ".join(cleaned)
        ticker_html = (joined + " <span class='dot'>&bull;</span> ") * 3

    st.markdown(
        f"""
        <div class="ticker-wrap">
          <div class="ticker-track">
            <span class="ticker-item">
              {ticker_html}
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