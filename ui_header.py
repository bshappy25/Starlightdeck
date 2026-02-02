import streamlit as st
import html

def render_header(ticker_items=None):
    """
    Starlight Deck header with animated constellation and slow-drift ticker.
    No Careon button - that's handled by the bubble module.
    """
    
    st.markdown(
        """
        <style>
        /* ========== HEADER CONSTELLATION ========== */
        .sld-constellation {
            position: relative;
            text-align: center;
            padding: 1.8rem 0 1.2rem 0;
            background: radial-gradient(
                ellipse 800px 400px at 50% -20%,
                rgba(180, 130, 255, 0.08),
                transparent 70%
            );
            overflow: hidden;
        }
        
        /* Floating stars background */
        .sld-constellation::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                radial-gradient(2px 2px at 20% 30%, rgba(255,255,255,0.3), transparent),
                radial-gradient(2px 2px at 60% 70%, rgba(180,130,255,0.4), transparent),
                radial-gradient(1px 1px at 50% 50%, rgba(120,220,210,0.3), transparent),
                radial-gradient(1px 1px at 80% 10%, rgba(246,193,119,0.4), transparent),
                radial-gradient(2px 2px at 90% 60%, rgba(255,255,255,0.2), transparent);
            background-size: 200% 200%;
            animation: starsFloat 28s ease-in-out infinite;
            pointer-events: none;
            opacity: 0.6;
        }
        
        @keyframes starsFloat {
            0%, 100% { transform: translate(0, 0); }
            33% { transform: translate(-3%, 2%); }
            66% { transform: translate(2%, -2%); }
        }
        
        /* Main title */
        .sld-title {
            font-size: 2.6rem;
            font-weight: 950;
            letter-spacing: 0.18em;
            background: linear-gradient(
                135deg,
                #ffd27a 0%,
                #f6c177 25%,
                #b482ff 50%,
                #78dcd2 75%,
                #ffd27a 100%
            );
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 12s ease infinite;
            filter: drop-shadow(0 4px 16px rgba(246,193,119,0.4));
            margin: 0;
            position: relative;
            z-index: 2;
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        /* Subtitle */
        .sld-subtitle {
            color: rgba(245,245,247,0.85);
            font-size: 0.98rem;
            line-height: 1.4rem;
            margin-top: 0.65rem;
            font-weight: 400;
            letter-spacing: 0.02em;
        }
        
        /* Sparkle divider */
        .sld-sparkles {
            font-size: 1.1rem;
            opacity: 0.7;
            letter-spacing: 0.8em;
            margin: 0.4rem 0 0.3rem 0;
            animation: sparkleGlow 3s ease-in-out infinite;
        }
        
        @keyframes sparkleGlow {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 0.9; }
        }
        
        /* ========== TICKER STREAM ========== */
        .ticker-shell {
            margin: 0.8rem auto 0.5rem auto;
            padding: 0;
            border-radius: 18px;
            background: linear-gradient(
                135deg,
                rgba(180, 130, 255, 0.08) 0%,
                rgba(120, 220, 210, 0.06) 100%
            );
            border: 1px solid rgba(255, 255, 255, 0.12);
            overflow: hidden;
            position: relative;
            max-width: 920px;
            backdrop-filter: blur(12px);
            box-shadow: 
                0 8px 32px rgba(0,0,0,0.15),
                inset 0 1px 0 rgba(255,255,255,0.08);
        }
        
        /* Subtle edge glow */
        .ticker-shell::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(246,193,119,0.4) 50%,
                transparent
            );
        }
        
        .ticker-track {
            display: inline-block;
            white-space: nowrap;
            will-change: transform;
            animation: tickerDrift 90s linear infinite;
            padding: 12px 0;
            padding-left: 100%;
        }
        
        @keyframes tickerDrift {
            from { transform: translateX(0); }
            to { transform: translateX(-100%); }
        }
        
        .ticker-content {
            display: inline-flex;
            align-items: center;
            gap: 16px;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-size: 0.92rem;
        }
        
        .ticker-dot {
            opacity: 0.45;
            margin: 0 18px;
            color: rgba(255,255,255,0.5);
        }
        
        /* Vibe colors with soft glow */
        .vibe-acuity {
            color: #59a6ff;
            text-shadow: 0 0 16px rgba(89,166,255,0.35);
        }
        
        .vibe-valor {
            color: #ff5b5b;
            text-shadow: 0 0 16px rgba(255,91,91,0.30);
        }
        
        .vibe-variety {
            color: #ffe27a;
            text-shadow: 0 0 16px rgba(255,226,122,0.30);
        }
        
        .phrase-text {
            color: rgba(245,245,247,0.92);
            text-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # ========== RENDER HEADER ==========
    st.markdown(
        """
        <div class="sld-constellation">
            <div class="sld-title">✦ STARLIGHT DECK ✦</div>
            <div class="sld-subtitle">
                A calm, reflective card experience<br/>
                guided by intuition and gentle structure
            </div>
            <div class="sld-sparkles">✧ ✦ ✧</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ========== BUILD TICKER STREAM ==========
    avv_pattern = (
        '<span class="vibe-acuity">ACUITY</span>'
        '<span class="ticker-dot">•</span>'
        '<span class="vibe-valor">VALOR</span>'
        '<span class="ticker-dot">•</span>'
        '<span class="vibe-variety">VARIETY</span>'
    )
    
    phrases = []
    if ticker_items:
        for item in ticker_items:
            clean = (item or "").strip()
            if clean:
                phrases.append(html.escape(clean[:48]))
    
    if not phrases:
        default_msg = "DONATE TO THE SLDNF TO ADD YOUR PHRASE"
        ticker_html = (
            f'<span class="phrase-text">{html.escape(default_msg)}</span>'
            f'<span class="ticker-dot">•</span>'
            f'{avv_pattern}'
            f'<span class="ticker-dot">•</span>'
            f'<span class="phrase-text">{html.escape(default_msg)}</span>'
        )
    else:
        segments = []
        for phrase in phrases:
            segments.append(f'<span class="phrase-text">{phrase}</span>')
            segments.append(avv_pattern)
        ticker_html = '<span class="ticker-dot">•</span>'.join(segments)
        ticker_html = (ticker_html + '<span class="ticker-dot">•</span>' + ticker_html)
    
    st.markdown(
        f"""
        <div class="ticker-shell">
            <div class="ticker-track">
                <span class="ticker-content">{ticker_html}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
