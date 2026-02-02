import streamlit as st

def get_vip_tier(balance: int) -> dict:
    """
    Calculate VIP tier based on balance.
    
    Tiers:
    - Seeker: 0-99 Ȼ
    - Wanderer: 100-299 Ȼ
    - Stargazer: 300-499 Ȼ
    - Luminary: 500+ Ȼ (VIP)
    """
    
    if balance >= 500:
        return {
            "name": "Luminary",
            "icon": "✦",
            "color": "#ffd27a",
            "glow": "rgba(246, 193, 119, 0.60)",
            "perks": ["Priority ticker placement", "Golden badge", "Exclusive zenith animation"]
        }
    elif balance >= 300:
        return {
            "name": "Stargazer",
            "icon": "✧",
            "color": "#b482ff",
            "glow": "rgba(180, 130, 255, 0.45)",
            "perks": ["Enhanced card glow", "Tier badge"]
        }
    elif balance >= 100:
        return {
            "name": "Wanderer",
            "icon": "✦",
            "color": "#78dcd2",
            "glow": "rgba(120, 220, 210, 0.40)",
            "perks": ["Tier badge"]
        }
    else:
        return {
            "name": "Seeker",
            "icon": "○",
            "color": "rgba(245, 245, 247, 0.70)",
            "glow": "rgba(255, 255, 255, 0.15)",
            "perks": []
        }


def render_vip_badge(balance: int, username: str = ""):
    """
    Render floating VIP status badge next to username.
    Shows tier, balance, and unlocked perks.
    """
    
    tier = get_vip_tier(balance)
    
    st.markdown(
        f"""
        <style>
        /* ========== VIP BADGE SYSTEM ========== */
        .vip-container {{
            display: inline-flex;
            align-items: center;
            gap: 12px;
            margin: 0.5rem 0;
        }}
        
        .vip-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 0.45em 0.95em;
            border-radius: 999px;
            background: linear-gradient(
                135deg,
                rgba(180, 130, 255, 0.12),
                rgba(120, 220, 210, 0.08)
            );
            border: 1px solid {tier['color']}40;
            font-weight: 900;
            font-size: 0.9rem;
            letter-spacing: 0.08em;
            color: {tier['color']};
            text-shadow: 0 0 12px {tier['glow']};
            box-shadow: 
                0 0 20px {tier['glow']},
                0 4px 12px rgba(0, 0, 0, 0.20);
            animation: badgeGlow 3s ease-in-out infinite;
        }}
        
        @keyframes badgeGlow {{
            0%, 100% {{ box-shadow: 0 0 16px {tier['glow']}, 0 4px 12px rgba(0, 0, 0, 0.20); }}
            50% {{ box-shadow: 0 0 28px {tier['glow']}, 0 4px 12px rgba(0, 0, 0, 0.20); }}
        }}
        
        .vip-icon {{
            font-size: 1.2rem;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.30));
        }}
        
        .vip-username {{
            font-size: 1.1rem;
            font-weight: 700;
            color: rgba(245, 245, 247, 0.90);
            letter-spacing: 0.05em;
        }}
        
        /* VIP perks tooltip */
        .vip-perks {{
            position: relative;
            display: inline-block;
            margin-left: 8px;
            cursor: help;
        }}
        
        .vip-perks-icon {{
            font-size: 0.85rem;
            opacity: 0.6;
            transition: opacity 0.2s ease;
        }}
        
        .vip-perks:hover .vip-perks-icon {{
            opacity: 1;
        }}
        
        .vip-perks-tooltip {{
            visibility: hidden;
            opacity: 0;
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(18, 10, 42, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 12px 16px;
            min-width: 200px;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.40);
            transition: all 0.3s ease;
            z-index: 10000;
        }}
        
        .vip-perks:hover .vip-perks-tooltip {{
            visibility: visible;
            opacity: 1;
        }}
        
        .vip-perks-title {{
            font-weight: 900;
            font-size: 0.85rem;
            color: {tier['color']};
            margin-bottom: 8px;
            letter-spacing: 0.06em;
        }}
        
        .vip-perk-item {{
            font-size: 0.8rem;
            color: rgba(245, 245, 247, 0.80);
            margin: 4px 0;
            padding-left: 12px;
            position: relative;
        }}
        
        .vip-perk-item::before {{
            content: '•';
            position: absolute;
            left: 0;
            color: {tier['color']};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Build perks list
    perks_html = ""
    if tier['perks']:
        perk_items = "".join([f'<div class="vip-perk-item">{p}</div>' for p in tier['perks']])
        perks_html = f"""
        <span class="vip-perks">
            <span class="vip-perks-icon">ℹ️</span>
            <div class="vip-perks-tooltip">
                <div class="vip-perks-title">PERKS UNLOCKED</div>
                {perk_items}
            </div>
        </span>
        """
    
    # Render badge
    username_display = f'<span class="vip-username">{username}</span>' if username else ""
    
    st.markdown(
        f"""
        <div class="vip-container">
            {username_display}
            <div class="vip-badge">
                <span class="vip-icon">{tier['icon']}</span>
                <span>{tier['name'].upper()}</span>
            </div>
            {perks_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def is_vip(balance: int) -> bool:
    """Check if user has VIP status (Luminary tier)."""
    return balance >= 500


def vip_zenith_animation():
    """
    Special zenith animation for VIP users.
    More dramatic visual effect.
    """
    
    st.markdown(
        """
        <style>
        @keyframes vipZenithBurst {
            0% {
                box-shadow: 0 0 20px rgba(246, 193, 119, 0.40);
                transform: scale(1);
            }
            50% {
                box-shadow: 
                    0 0 60px rgba(246, 193, 119, 0.80),
                    0 0 120px rgba(180, 130, 255, 0.40);
                transform: scale(1.05);
            }
            100% {
                box-shadow: 0 0 20px rgba(246, 193, 119, 0.40);
                transform: scale(1);
            }
        }
        
        .vip-zenith-effect {
            animation: vipZenithBurst 1.5s ease-out;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
