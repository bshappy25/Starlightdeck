import streamlit as st
import base64

def render_audio_controls():
    """
    Ambient soundscape system with toggle controls.
    Provides infrastructure for background audio + sound effects.
    """
    
    st.session_state.setdefault("audio_enabled", False)
    st.session_state.setdefault("sfx_enabled", True)
    
    st.markdown(
        """
        <style>
        /* ========== AUDIO CONTROL PANEL ========== */
        .audio-shrine {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        /* Audio orb button */
        .audio-orb {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: linear-gradient(
                135deg,
                rgba(180, 130, 255, 0.18),
                rgba(120, 220, 210, 0.14)
            );
            border: 1.5px solid rgba(255, 255, 255, 0.20);
            backdrop-filter: blur(12px);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 
                0 4px 16px rgba(0, 0, 0, 0.25),
                0 0 24px rgba(180, 130, 255, 0.15);
        }
        
        .audio-orb:hover {
            transform: scale(1.08);
            box-shadow: 
                0 6px 24px rgba(0, 0, 0, 0.30),
                0 0 36px rgba(180, 130, 255, 0.30);
            border-color: rgba(246, 193, 119, 0.40);
        }
        
        .audio-orb.active {
            background: linear-gradient(
                135deg,
                rgba(246, 193, 119, 0.22),
                rgba(180, 130, 255, 0.18)
            );
            box-shadow: 
                0 0 28px rgba(246, 193, 119, 0.45),
                0 4px 16px rgba(0, 0, 0, 0.25);
            animation: audioPulse 2s ease-in-out infinite;
        }
        
        @keyframes audioPulse {
            0%, 100% { box-shadow: 0 0 20px rgba(246, 193, 119, 0.35); }
            50% { box-shadow: 0 0 40px rgba(246, 193, 119, 0.60); }
        }
        
        .audio-icon {
            font-size: 1.3rem;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.30));
        }
        
        /* Mini control panel (appears on hover) */
        .audio-panel {
            background: rgba(18, 10, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 12px;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.40);
            min-width: 180px;
            opacity: 0;
            pointer-events: none;
            transform: translateY(10px);
            transition: all 0.3s ease;
        }
        
        .audio-shrine:hover .audio-panel {
            opacity: 1;
            pointer-events: all;
            transform: translateY(0);
        }
        
        .audio-option {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0;
            color: rgba(245, 245, 247, 0.85);
            font-size: 0.9rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .audio-option:last-child {
            border-bottom: none;
        }
        
        .audio-label {
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        
        .audio-toggle {
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .audio-toggle:hover {
            transform: scale(1.15);
        }
        
        /* Hidden audio elements */
        .sld-audio-player {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # ========== SOUND FILES (Base64 or URLs) ==========
    # For now, we'll use data URIs or external CDN links
    # You can replace these with actual hosted audio files
    
    AMBIENT_TRACK = None  # Add base64 or URL here when ready
    
    # ========== RENDER CONTROLS ==========
    audio_active = st.session_state.get("audio_enabled", False)
    sfx_active = st.session_state.get("sfx_enabled", True)
    
    icon = "🔊" if audio_active else "🔇"
    active_class = "active" if audio_active else ""
    
    # Audio player (hidden, controlled by JS)
    if AMBIENT_TRACK and audio_active:
        st.markdown(
            f"""
            <audio id="sld-ambient" class="sld-audio-player" loop autoplay>
                <source src="{AMBIENT_TRACK}" type="audio/mpeg">
            </audio>
            """,
            unsafe_allow_html=True
        )
    
    # Floating control shrine
    st.markdown(
        f"""
        <div class="audio-shrine">
            <div class="audio-panel">
                <div class="audio-option">
                    <span class="audio-label">Ambient</span>
                    <span class="audio-toggle" onclick="toggleAudio()">
                        {'✓' if audio_active else '○'}
                    </span>
                </div>
                <div class="audio-option">
                    <span class="audio-label">SFX</span>
                    <span class="audio-toggle" onclick="toggleSFX()">
                        {'✓' if sfx_active else '○'}
                    </span>
                </div>
            </div>
            <div class="audio-orb {active_class}">
                <span class="audio-icon">{icon}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Toggle buttons (hidden, controlled by JS clicks)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊", key="audio_toggle_hidden", help="Toggle ambient sound"):
            st.session_state["audio_enabled"] = not audio_active
            st.rerun()
    with col2:
        if st.button("✨", key="sfx_toggle_hidden", help="Toggle sound effects"):
            st.session_state["sfx_enabled"] = not sfx_active
            st.rerun()


def play_sfx(sound_type: str):
    """
    Trigger sound effects based on events.
    
    Args:
        sound_type: 'draw', 'zenith', 'estrella', 'careon', 'success', 'failure'
    """
    
    if not st.session_state.get("sfx_enabled", True):
        return
    
    # Sound effect mapping (replace with actual files)
    SFX_MAP = {
        "draw": None,      # Soft chime
        "zenith": None,    # Crystal shimmer
        "estrella": None,  # Deep hum
        "careon": None,    # Coin clink
        "success": None,   # Ascending tone
        "failure": None    # Gentle descending
    }
    
    sfx_url = SFX_MAP.get(sound_type)
    
    if sfx_url:
        st.markdown(
            f"""
            <audio autoplay>
                <source src="{sfx_url}" type="audio/mpeg">
            </audio>
            """,
            unsafe_allow_html=True
        )


def audio_ready() -> bool:
    """Check if audio system is enabled."""
    return st.session_state.get("audio_enabled", False)
