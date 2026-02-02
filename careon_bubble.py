import streamlit as st

def render_bubble():
    """
    Ethereal floating Careon bubble that toggles the market.
    Gradient shimmer + pulse animation.
    """
    
    st.session_state.setdefault("show_market", False)
    is_open = st.session_state.get("show_market", False)
    
    st.markdown(
        """
        <style>
        /* ========== BUBBLE CONTAINER ========== */
        .careon-orb-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 1.2rem 0 0.8rem 0;
            position: relative;
        }
        
        /* Ambient glow ring */
        .careon-orb-container::before {
            content: '';
            position: absolute;
            width: 140px;
            height: 140px;
            border-radius: 50%;
            background: radial-gradient(
                circle,
                rgba(246,193,119,0.15) 0%,
                rgba(180,130,255,0.08) 50%,
                transparent 70%
            );
            animation: ambientPulse 4s ease-in-out infinite;
            pointer-events: none;
        }
        
        @keyframes ambientPulse {
            0%, 100% { transform: scale(1); opacity: 0.6; }
            50% { transform: scale(1.15); opacity: 0.9; }
        }
        
        /* ========== BUTTON STYLING ========== */
        .careon-orb-container .stButton {
            position: relative;
            z-index: 2;
        }
        
        .careon-orb-container .stButton > button {
            width: auto !important;
            padding: 0.72em 1.45em !important;
            border-radius: 999px !important;
            
            background: linear-gradient(
                135deg,
                rgba(246, 193, 119, 0.20) 0%,
                rgba(180, 130, 255, 0.16) 50%,
                rgba(120, 220, 210, 0.14) 100%
            ) !important;
            background-size: 200% 200% !important;
            
            color: #ffd27a !important;
            font-weight: 960 !important;
            font-size: 1.05rem !important;
            letter-spacing: 0.12em !important;
            
            border: 1.5px solid rgba(246, 193, 119, 0.45) !important;
            
            box-shadow:
                0 0 24px rgba(246, 193, 119, 0.55),
                0 0 48px rgba(180, 130, 255, 0.20),
                0 4px 16px rgba(0, 0, 0, 0.25),
                inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
            
            text-shadow: 
                0 0 18px rgba(246, 193, 119, 0.50),
                0 2px 4px rgba(0, 0, 0, 0.40) !important;
            
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            animation: gradientShimmer 6s ease infinite, floatBubble 3s ease-in-out infinite;
            cursor: pointer;
        }
        
        @keyframes gradientShimmer {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        @keyframes floatBubble {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-4px); }
        }
        
        /* Hover state */
        .careon-orb-container .stButton > button:hover {
            transform: translateY(-3px) scale(1.06) !important;
            
            box-shadow:
                0 0 36px rgba(246, 193, 119, 0.85),
                0 0 72px rgba(180, 130, 255, 0.35),
                0 0 96px rgba(120, 220, 210, 0.20),
                0 6px 24px rgba(0, 0, 0, 0.30),
                inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
            
            border-color: rgba(246, 193, 119, 0.70) !important;
            filter: brightness(1.10);
            animation: none;
        }
        
        /* Active/open state indicator */
        .careon-orb-container .stButton > button.open-state {
            background: linear-gradient(
                135deg,
                rgba(246, 193, 119, 0.30) 0%,
                rgba(180, 130, 255, 0.26) 50%,
                rgba(120, 220, 210, 0.22) 100%
            ) !important;
            box-shadow:
                0 0 28px rgba(246, 193, 119, 0.75),
                0 0 56px rgba(180, 130, 255, 0.30),
                0 4px 20px rgba(0, 0, 0, 0.28) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Button label with indicator
    label = "Careon Ȼ" + (" ✦" if is_open else "")
    
    st.markdown('<div class="careon-orb-container">', unsafe_allow_html=True)
    
    if st.button(label, key="__sld_careon_bubble_toggle"):
        st.session_state["show_market"] = not is_open
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
