import os
import random
import streamlit as st
import codes_ledger
import careon_bank_v2 as bank

# Try importing genai
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    st.warning("google-generativeai not installed")

# ---------- Paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "careon_bank_v2.json")
LEDGER_PATH = os.path.join(HERE, "codes_ledger.json")

# ---------- API Setup ----------
GEMINI_API_KEY = None

if GENAI_AVAILABLE:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.sidebar.warning(f"API key issue: {e}")

# ---------- Page config ----------
st.set_page_config(page_title="Starlight Deck", layout="centered")




import os
import random
import streamlit as st

import codes_ledger

import careon_bank_v2 as bank

# ---------- Paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "careon_bank_v2.json")
LEDGER_PATH = os.path.join(HERE, "codes_ledger.json")
# ---------- Page config ----------
st.set_page_config(page_title="Starlight Deck", layout="centered")

# ---------- Style ----------

# ---------- UI Header ----------
st.markdown(
    """
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<div class='muted' style='text-align:center; margin-bottom: 0.45em;'>"
    "A calm, reflective card experience<br/>guided by intuition and gentle structure."
    "</div>",
    unsafe_allow_html=True
)

# Ticker (no unicode bullets; uses &bull;)
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
          <span class="variety">VARIETY</span><span class="dot">&bull;</span>
          <span class="acuity">ACUITY</span><span class="dot">&bull;</span>
          <span class="valor">VALOR</span><span class="dot">&bull;</span>
          <span class="variety">VARIETY</span><span class="dot">&bull;</span>
        </span>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Clickable Careon pill (purchase placeholder)
st.markdown(
    """
    <div class='careon-pill-wrap'>
        <a href="#"
           class="careon-pill"
           style="text-decoration:none;"
           title="Purchase Careons (coming soon)">
            Careon Ȼ
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### Deposit Codes")

redeem_code = st.text_input("Redeem code", placeholder="DEP-50-XXXXXX", key="redeem_code_input")
if st.button("Redeem", key="redeem_btn"):
    ok, msg, amt = codes_ledger.redeem_code(LEDGER_PATH, redeem_code, redeemer="web")
    if ok:
        deposit_into_bank(amt, f"Deposit redeemed: +{amt} Ȼ (code)")
        st.success(f"{msg} +{amt} Ȼ added.")
        st.rerun()
    else:
        st.error(msg)

st.markdown("---")

st.markdown(
    "<div class='muted'>Admin: <b>bshapp</b></div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        text-align:center;
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: 0.12em;
        color: #ffd27a;
        text-shadow:
            0 2px 8px rgba(0,0,0,0.6),
            0 0 22px rgba(246,193,119,0.55),
            0 0 48px rgba(246,193,119,0.25);
        margin-top: 0.4em;
    ">
        ✦ STARLIGHT DECK ✦
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("### Admin")

# Admin login (password checked against secrets/env)
admin_pw = st.text_input("Admin password", type="password", key="admin_pw_input")
if st.button("Unlock Admin", key="admin_unlock_btn"):
    secret_pw = None
    try:
        secret_pw = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        secret_pw = None
    if not secret_pw:
        secret_pw = os.getenv("SLD_ADMIN_PASSWORD")

    if secret_pw and admin_pw == secret_pw:
        st.session_state["admin_ok"] = True
        st.success("Admin unlocked.")
        st.rerun()
    else:
        st.session_state["admin_ok"] = False
        st.error("Wrong password.")

if st.session_state.get("admin_ok"):
    st.markdown("#### Generate deposit code")
    amt = st.selectbox("Amount", [25, 50, 100, 250], index=1, key="gen_amt")
    if st.button("Generate Code", key="gen_code_btn"):
        new_code = codes_ledger.add_code(LEDGER_PATH, int(amt))
        st.code(new_code)
        st.info("Give this code to a user. It can be redeemed once.")

    st.markdown("#### Devtool (Admin only)")
    dev = st.text_input("Devtool code", placeholder="TGIF", key="admin_devtool_input")
    if st.button("Apply Devtool", key="admin_devtool_apply"):
        if (dev or "").strip().upper() == "TGIF":
            # TGIF adds +5 to balance (and optionally network fund — you choose)
            # I recommend: balance only (dev/test), NOT network fund.
            b2 = bank.load_bank(BANK_PATH)
            b2["balance"] = int(b2.get("balance", 0)) + 5
            b2.setdefault("history", [])
            b2["history"].append("TGIF (admin): +5 Ȼ")
            bank.save_bank(b2, BANK_PATH)
            st.success("TGIF applied: +5 Ȼ")
            st.rerun()
        else:
            st.error("Unknown devtool code.")

# ---------- Admin: Community Reward ----------
b = bank.load_bank(BANK_PATH)
if b.get("sld_network_fund", 0) >= 1000:
    st.markdown("#### 🎁 Community Reward")

    if st.button("Generate 20Ȼ Reward Code", key="gen_reward_code"):
        reward_code = codes_ledger.add_code(LEDGER_PATH, 20)
        st.code(reward_code)
        st.info("Reward code generated. Share intentionally.")
else:
    st.markdown(
        "<div class='muted'>Community reward unlocks at 1000 Ȼ.</div>",
        unsafe_allow_html=True
    )

# ---------- Helpers ----------
def deposit_into_bank(amount: int, note: str) -> None:
    """
    Deposit policy:
    - 95% goes to user balance
    - 5% goes to SLD Network Fund
    """
    amount = int(amount)
    if amount <= 0:
        return

    network_cut = amount // 20        # 5%
    user_amount = amount - network_cut

    b = bank.load_bank(BANK_PATH)

    b["balance"] = int(b.get("balance", 0)) + user_amount
    b["sld_network_fund"] = int(b.get("sld_network_fund", 0)) + network_cut

    b.setdefault("history", [])
    b["history"].append(
        f"Deposit redeemed: +{user_amount} Ȼ (network +{network_cut} Ȼ)"
    )

    bank.save_bank(b, BANK_PATH)


def is_admin() -> bool:
    """
    Admin gate:
    - Uses Streamlit secrets if present: st.secrets["ADMIN_PASSWORD"]
    - Else uses env var: SLD_ADMIN_PASSWORD
    """
    pw = None
    try:
        pw = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        pw = None
    if not pw:
        pw = os.getenv("SLD_ADMIN_PASSWORD")
    if not pw:
        return False
    return st.session_state.get("admin_ok", False)

def rapid_zenith_roll(trials: int = 20, chance: float = 0.05) -> bool:
    return any(random.random() < chance for _ in range(trials))

def ensure_bank_exists():
    """
    If the bank file doesn't exist or is corrupted, reset it safely.
    """
    try:
        _ = bank.load_bank(BANK_PATH)
    except Exception:
        b0 = {"balance": 25, "sld_network_fund": 0, "history": []}
        bank.save_bank(b0, BANK_PATH)

def reset_bank_file():
    b0 = {"balance": 25, "sld_network_fund": 0, "history": []}
    bank.save_bank(b0, BANK_PATH)

def push_history_line(b: dict, line: str, keep: int = 12) -> None:
    b.setdefault("history", [])
    b["history"].append(line)
    if len(b["history"]) > keep:
        b["history"] = b["history"][-keep:]

# ---------- Init ----------
ensure_bank_exists()

# ---------- Session state ----------
st.session_state.setdefault("last_result", None)   # ("SUCCESS"/"FAILURE", estrella_line)
st.session_state.setdefault("last_roll", None)     # bool success
st.session_state.setdefault("devtool_msg", None)

# ---------- Load persistent bank ----------
b = bank.load_bank(BANK_PATH)

# ---------- Sidebar (controls + TGIF devtool) ----------
with st.sidebar:
    st.markdown("### Controls")

    # Reset wallet
    if st.button("Reset Wallet (25 Ȼ)", key="sb_reset_wallet"):
        reset_bank_file()
        st.session_state["last_result"] = None
        st.session_state["last_roll"] = None
        st.session_state["devtool_msg"] = "Wallet reset to 25 Ȼ."
        st.rerun()

    st.markdown("---")

    st.markdown("### Devtool")
    st.markdown("<div class='muted'>Enter <b>TGIF</b> to add <b>+5 Ȼ</b>.</div>", unsafe_allow_html=True)

    dev_input = st.text_input("Devtool code", value="", placeholder="TGIF", key="devtool_input")
    if st.button("Apply Devtool", key="sb_apply_devtool"):
        code = (dev_input or "").strip().upper()
        b2 = bank.load_bank(BANK_PATH)

        if code == "TGIF":
            # Award +5 and log it
            bank.award_once_per_round(b2, note="devtool-tgif", amount=5)
            push_history_line(b2, "TGIF applied: +5 Ȼ")
            bank.save_bank(b2, BANK_PATH)
            st.session_state["devtool_msg"] = "✅ TGIF applied: +5 Ȼ"
            st.rerun()
        else:
            st.session_state["devtool_msg"] = "❌ Unknown code."
            st.rerun()

    if st.session_state.get("devtool_msg"):
        st.info(st.session_state["devtool_msg"])

    st.markdown("---")
    st.markdown("### About")
    st.markdown("<div class='muted'>Community-powered • Early test build</div>", unsafe_allow_html=True)

# ---------- UI ----------
## ---------- Style (Refreshed UI) ----------
st.markdown(
    r"""
    <style>
    :root {
        --bg1: #120A2A;   /* deep purple */
        --bg2: #1A0F3D;
        --panel: rgba(255,255,255,0.06);
        --panelBorder: rgba(255,255,255,0.10);
        --gold: #f6c177;
        --gold2: #ffd27a;
        --text: #f5f5f7;
        --muted: rgba(245,245,247,0.82);
        --btn: #3f44c8;
        --btnHover: #5a5ff0;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 50% -10%, rgba(255, 210, 122, 0.12), transparent 60%),
                    linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
        color: var(--text);
    }

    /* text helpers */
    .muted { color: var(--muted); font-size: 0.95rem; }

    /* Cards */
    .cardbox {
        background: var(--panel);
        border: 1px solid var(--panelBorder);
        border-radius: 16px;
        padding: 14px 16px;
        margin-top: 12px;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--btn);
        color: white;
        border-radius: 14px;
        padding: 0.65em 1.2em;
        border: none;
        font-size: 1.05rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover { background-color: var(--btnHover); transform: scale(1.01); }

    /* Careon pill */
    .careon-pill-wrap { text-align:center; margin-top: 0.9em; margin-bottom: 0.6em; }

    .careon-pill {
        display: inline-block;
        padding: 0.42em 0.95em;
        border-radius: 999px;
        background: rgba(246, 193, 119, 0.14);
        color: var(--gold2);
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
    .careon-pill:hover {
        transform: translateY(-1px) scale(1.04);
        box-shadow:
            0 0 22px rgba(246,193,119,0.85),
            0 0 52px rgba(246,193,119,0.45);
    }

    @keyframes careonPulse {
        0% {
            transform: translateY(0px);
            box-shadow:
                0 0 12px rgba(246,193,119,0.45),
                0 0 28px rgba(246,193,119,0.20);
        }
        50% {
            transform: translateY(-1px);
            box-shadow:
                0 0 18px rgba(246,193,119,0.78),
                0 0 44px rgba(246,193,119,0.33);
        }
        100% {
            transform: translateY(0px);
            box-shadow:
                0 0 12px rgba(246,193,119,0.45),
                0 0 28px rgba(246,193,119,0.20);
        }
    }

    /* ---------- Moving Banner (Acuity / Valor / Variety) ---------- */
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
        animation: tickerScroll 22s linear infinite; /* slower = more zen */
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

    .acuity { color: #59a6ff; text-shadow: 0 0 14px rgba(89,166,255,0.22); }
    .valor  { color: #ff5b5b; text-shadow: 0 0 14px rgba(255,91,91,0.18); }
    .variety{ color: #ffe27a; text-shadow: 0 0 14px rgba(255,226,122,0.18); }

    .footer { text-align: center; opacity: 0.75; font-size: 0.85rem; margin-top: 2em; }
    </style>
    """,
    unsafe_allow_html=True
)
# Status box

# ---------- Soft Goal ----------
b = bank.load_bank(BANK_PATH)
goal = 1000
current = int(b.get("sld_network_fund", 0))
progress_pct = min(100, int((current / goal) * 100))

st.markdown(
    f"""
    <div class="cardbox" style="text-align:center;">
        <b>Community Goal:</b> {current} / {goal} Ȼ<br/>
        <div class="muted" style="margin-top:0.3em;">
            When the network reaches {goal} Ȼ, a reward code may be released.
        </div>
        <div style="
            margin-top:0.6em;
            height:10px;
            background: rgba(255,255,255,0.08);
            border-radius: 999px;
            overflow:hidden;
        ">
            <div style="
                width:{progress_pct}%;
                height:100%;
                background: linear-gradient(90deg, #f6c177, #ffd27a);
                box-shadow: 0 0 12px rgba(246,193,119,0.6);
            "></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

b = bank.load_bank(BANK_PATH)
st.markdown(
    f"""
    <div class="cardbox" style="text-align:center;">
        <b>Balance:</b> {b.get("balance", 0)} Ȼ &nbsp;&nbsp; • &nbsp;&nbsp;
        <b>🌐 SLD Network Fund:</b> {b.get("sld_network_fund", 0)} Ȼ
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

st.divider()

# ---------- Classic Draw Mode ----------
st.subheader("🌟 Classic Draw Mode")

st.write("Cost: **1 Ȼ** • Experience: **20 cards** • Estrella speaks at **10 & 20**")
st.write("Draw cards mindfully. Reflect. Build your question.")

if st.button("Start Classic Journey (-1 Ȼ)", key="classic_start"):
    b = bank.load_bank(BANK_PATH)
    
    if b.get("balance", 0) < 1:
        st.error("Need 1 Ȼ to start Classic Mode.")
    else:
        if bank.spend(b, 1, note="classic charge"):
            st.session_state["classic_active"] = True
            st.session_state["classic_draws"] = 0
            st.session_state["classic_vibe_counts"] = {"acuity": 0, "valor": 0, "variety": 0}
            st.session_state["classic_level_counts"] = {1: 0, 2: 0, 3: 0}
            st.session_state["classic_zenith_count"] = 0
            push_history_line(b, "Classic Mode started: -1 Ȼ")
            bank.save_bank(b, BANK_PATH)
            st.rerun()

# Classic session UI
if st.session_state.get("classic_active"):
    draws = st.session_state["classic_draws"]
    
    st.markdown(f"**Progress:** {draws}/20 cards")
    
    # Vibe counters
    vc = st.session_state["classic_vibe_counts"]
    st.markdown(f"🔵 Acuity: {vc['acuity']} | 🔴 Valor: {vc['valor']} | 🟡 Variety: {vc['variety']}")
    
    if draws < 20:
        if st.button("✨ Draw Card ✨", key=f"classic_draw_{draws}"):
            # Draw logic
            vibes = ["acuity", "valor", "variety"]
            vibe = random.choice(vibes)
            
            roll = random.randint(1, 100)
            if roll <= 75:
                level = 1
            elif roll <= 95:
                level = 2
            else:
                level = 3
            
            zenith = random.random() < 0.05
            
            # Update counts
            st.session_state["classic_draws"] += 1
            st.session_state["classic_vibe_counts"][vibe] += 1
            st.session_state["classic_level_counts"][level] += 1
            if zenith:
                st.session_state["classic_zenith_count"] += 1
            
            # Display card
            vibe_colors = {"acuity": "#59a6ff", "valor": "#ff5b5b", "variety": "#ffe27a"}
            vibe_emoji = {"acuity": "🔵", "valor": "🔴", "variety": "🟡"}
            level_names = {1: "Common", 2: "Rare", 3: "Legendary"}
            
            zenith_text = "◇ ZENITH ◇" if zenith else ""
            
            st.markdown(
                f"""
                <div class="cardbox" style="border: 2px solid {vibe_colors[vibe]};">
                    <div style="text-align:center; font-size:1.8rem;">
                        {vibe_emoji[vibe]} {vibe.upper()}
                    </div>
                    <div style="text-align:center; margin-top:0.5em;">
                        Level {level} - {level_names[level]}
                    </div>
                    <div style="text-align:center; color:#ffd27a; margin-top:0.5em; font-weight:900;">
                        {zenith_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Estrella at card 10
            if st.session_state["classic_draws"] == 10:
                if "estrella_10_response" not in st.session_state:
                    st.markdown("### ✨ Estrella ✨")
                    st.markdown("*10-card reflection...*")
                    
                    if GEMINI_API_KEY:
                        try:
                            model = genai.GenerativeModel('gemini-3-flash-preview')
                            vc = st.session_state['classic_vibe_counts']
                            lc = st.session_state['classic_level_counts']
                            prompt = f"Two short paragraphs analyzing the journey.\nVibes: Acuity {vc['acuity']}, Valor {vc['valor']}, Variety {vc['variety']}\nLevels: {dict(lc)}\nZenith: {st.session_state['classic_zenith_count']}"
                            response = model.generate_content(prompt)
                            st.session_state["estrella_10_response"] = response.text
                            
                            # Award Careon
                            b = bank.load_bank(BANK_PATH)
                            bank.award_once_per_round(b, note="classic-10-estrella", amount=1)
                            push_history_line(b, "Estrella spoke (10): +1 Ȼ")
                            bank.save_bank(b, BANK_PATH)
                        except Exception as e:
                            st.session_state["estrella_10_response"] = f"Estrella is resting ({str(e)})"
                    else:
                        st.session_state["estrella_10_response"] = "Add GEMINI_API_KEY to hear Estrella's wisdom"
                
                # Always display if it exists
                if "estrella_10_response" in st.session_state:
                    st.markdown("### ✨ Estrella ✨")
                    st.markdown(f"<div class='cardbox'>{st.session_state['estrella_10_response']}</div>", unsafe_allow_html=True)
            
            st.rerun()
    
    # Card 20 finale
    if draws == 20:
        if "estrella_20_response" not in st.session_state:
            st.markdown("### ✨ Estrella ✨")
            st.markdown("*Journey complete. 20-card analysis...*")
            
            if GEMINI_API_KEY:
                try:
                    model = genai.GenerativeModel('gemini-3-flash-preview')

                    prompt = f"Two short paragraphs analyzing the journey.\nVibes: {st.session_state['classic_vibe_counts']}\nLevels: {st.session_state['classic_level_counts']}\nZenith: {st.session_state['classic_zenith_count']}"
                    response = model.generate_content(prompt)
                    st.session_state["estrella_20_response"] = response.text
                    
                    # Award Careon
                    b = bank.load_bank(BANK_PATH)
                    bank.award_once_per_round(b, note="classic-20-estrella", amount=1)
                    push_history_line(b, "Estrella spoke (20): +1 Ȼ")
                    bank.save_bank(b, BANK_PATH)
                except Exception as e:
                    st.session_state["estrella_20_response"] = f"Estrella is resting ({str(e)})"
            else:
                st.session_state["estrella_20_response"] = "Add GEMINI_API_KEY to hear Estrella's wisdom"
        
        # Always display if it exists
        if "estrella_20_response" in st.session_state:
            st.markdown("### ✨ Estrella ✨")
            st.markdown(f"<div class='cardbox'>{st.session_state['estrella_20_response']}</div>", unsafe_allow_html=True)
        
        # Final question
        final_q = st.text_input("Ask Estrella your final question:", key="classic_final_q")
        if st.button("Submit Question", key="classic_submit_q"):
            if final_q and GEMINI_API_KEY:
                try:
                    model = genai.GenerativeModel('gemini-3-flash-preview')

                    prompt = f"Return exactly five lines:\nIntention:\nForward action:\nPast reflection:\nEnergy level:\nAspirational message:\n\nStats: {st.session_state['classic_vibe_counts']}\nQuestion: {final_q}"
                    response = model.generate_content(prompt)
                    st.session_state["estrella_final_response"] = response.text
                    
                    # Award final Careon
                    b = bank.load_bank(BANK_PATH)
                    bank.award_once_per_round(b, note="classic-final-q", amount=1)
                    push_history_line(b, "Journey complete: +1 Ȼ")
                    bank.save_bank(b, BANK_PATH)
                    
                    st.session_state["classic_active"] = False
                    st.success("Journey complete! Net: +2 Ȼ")
                except Exception as e:
                    st.error(f"Estrella cannot respond ({str(e)})")
        
        # Display final response if exists
        if "estrella_final_response" in st.session_state:
            st.markdown(f"<div class='cardbox'>{st.session_state['estrella_final_response']}</div>", unsafe_allow_html=True)

# ---------- Rapid Mode (primary product for now) ----------
st.subheader("⚡ Rapid Mode")

st.write("Cost: **5 Ȼ** • Roll: **20 pulses @ 5%** • Win condition: **≥ 1 Zenith**")
st.write("Success payout: **+20 Ȼ** + **+3 Ȼ completion** • Failure payout: **+1 Ȼ completion**")

cA, cB = st.columns(2)
run = cA.button("Run Rapid (-5 Ȼ)", key="rapid_run")
clear = cB.button("Clear Result", key="rapid_clear_result")

if clear:
    st.session_state["last_result"] = None
    st.session_state["last_roll"] = None
    st.rerun()

if run:
    b = bank.load_bank(BANK_PATH)

    if b.get("balance", 0) < 5:
        st.error("Not enough Careons to run Rapid Mode.")
    else:
        # ALL spend funds the network (handled in bank.spend if implemented that way)
        if not bank.spend(b, 5, note="rapid charge"):
            st.error("Not enough Careons to run Rapid Mode.")
        else:
            success = rapid_zenith_roll(trials=20, chance=0.05)
            st.session_state["last_roll"] = success

            if success:
                estrella_line = "★ Estrella ★ Bold move, you will be rewarded kindly."
                bank.award_once_per_round(b, note="rapid-success-20", amount=20)
                bank.award_once_per_round(b, note="rapid-completion-bonus", amount=3)
                st.session_state["last_result"] = ("SUCCESS", estrella_line)
                push_history_line(b, "Rapid SUCCESS: +20 Ȼ +3 Ȼ")
            else:
                estrella_line = "★ Estrella ★ Recklessness can be costly."
                bank.award_once_per_round(b, note="rapid-fail-completion", amount=1)
                st.session_state["last_result"] = ("FAILURE", estrella_line)
                push_history_line(b, "Rapid FAILURE: +1 Ȼ")

            bank.save_bank(b, BANK_PATH)
            st.rerun()

# ---------- Result display ----------
if st.session_state["last_result"]:
    status, estrella_line = st.session_state["last_result"]

    if status == "SUCCESS":
        st.success(status)
    else:
        st.warning(status)

    result_html = f'<div class="cardbox"><div style="font-size:1.15rem;"><b>{estrella_line}</b></div></div>'
    st.markdown(result_html, unsafe_allow_html=True)

    # Optional detail line
    if st.session_state.get("last_roll") is not None:
        roll_text = "Zenith appeared ✅" if st.session_state["last_roll"] else "No Zenith ❌"
        st.markdown(f"<div class='cardbox'><b>Roll:</b> {roll_text}</div>", unsafe_allow_html=True)

st.divider()

# ---------- Recent history ----------
b = bank.load_bank(BANK_PATH)
hist = b.get("history", []) or []
st.markdown("<div class='cardbox'><b>Recent Activity</b></div>", unsafe_allow_html=True)

if hist:
    # Show newest first
    for line in reversed(hist[-12:]):
        st.markdown(f"<div class='cardbox'>{line}</div>", unsafe_allow_html=True)
else:
    st.caption("No activity yet. Run Rapid Mode to begin.")

st.markdown('<div class="footer">Community-powered • Early test build</div>', unsafe_allow_html=True)