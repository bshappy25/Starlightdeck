import os
import streamlit as st

# -------------------------
# CORE MODULES
# -------------------------
import careon_bank_v2 as bank
import ui_header
import careon_bubble
import careon_market

# -------------------------
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# -------------------------
st.set_page_config(
    page_title="Starlight Deck",
    layout="centered"
)

# -------------------------
# PATHS
# -------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "careon_bank_v2.json")

# -------------------------
# ENSURE BANK FILE EXISTS
# -------------------------
b = bank.load_bank(BANK_PATH)
bank.save_bank(b, BANK_PATH)

# -------------------------
# SESSION STATE DEFAULTS
# -------------------------
st.session_state.setdefault("show_market", False)

# -------------------------
# BUILD TICKER PHRASES
# -------------------------
b_for_ticker = bank.load_bank(BANK_PATH)
phrases = []

for tx in reversed(b_for_ticker.get("history", []) or []):
    if isinstance(tx, dict) and tx.get("type") == "phrase":
        meta = tx.get("meta") or {}
        msg = (meta.get("msg") or "").strip()
        usr = (meta.get("user") or "").strip()
        if msg:
            label = f"{usr.upper()}: {msg}" if usr else msg
            phrases.append(label)
    if len(phrases) >= 10:
        break

# -------------------------
# TOP UI (HEADER + CAREON MARKET)
# -------------------------
ui_header.render_header(ticker_items=phrases)
careon_bubble.render_bubble()
careon_market.render_market(bank, BANK_PATH)

# -------------------------
# DIVIDER — EVERYTHING BELOW IS CONTENT
# -------------------------
st.divider()


st.divider()

# PASTE COMMUNITY BLOCK HERE

st.info("⚙️ Stabilizing build: content below temporarily paused.")
st.stop()

# -------------------------
# OPTIONAL GEMINI (Estrella)
# -------------------------
GEMINI_API_KEY = None
GENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

if GENAI_AVAILABLE:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        GEMINI_API_KEY = None
        st.sidebar.warning(f"Gemini key issue: {e}")
else:
    st.sidebar.info("Gemini not installed — Estrella will be offline.")

# -------------------------
# HELPERS (defined BEFORE UI)
# -------------------------
def get_admin_secret() -> str | None:
    try:
        pw = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        pw = None
    if not pw:
        pw = os.getenv("SLD_ADMIN_PASSWORD")
    return pw

def gemini_ready() -> bool:
    return GENAI_AVAILABLE and bool(st.secrets.get("GEMINI_API_KEY", None))

def get_gemini_model():
    if not GENAI_AVAILABLE:
        return None
    try:
        key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=key)
        return genai.GenerativeModel(MODEL_NAME)
    except Exception:
        return None

def deposit_into_bank(amount: int, note: str) -> None:
    """
    Deposit policy:
      - 95% to user balance
      - 5% to SLD network fund
    """
    amount = int(amount)
    if amount <= 0:
        return

    network_cut = amount // 20  # 5%
    user_amount = amount - network_cut

    b = bank.load_bank(BANK_PATH)
    
    # -----------------------------
# Phrase input (<= 20 chars)
# -----------------------------
# -----------------------------
# Donate-to-submit phrase (100Ȼ)
# -----------------------------
st.session_state.setdefault("show_phrase_box", False)

if st.button("🤝 Donate to the community (SLDNF)", key="btn_donate_open"):
    st.session_state["show_phrase_box"] = True

if st.session_state.get("show_phrase_box"):
    st.markdown("### Community Phrase")
    st.caption("Max 20 characters • Costs 100Ȼ • Your donation funds the SLD Network Fund (SLDNF).")

    new_phrase = st.text_input("Your phrase", max_chars=20, key="phrase_add_input")

    c1, c2 = st.columns(2)
    submit = c1.button("Submit Phrase (-100Ȼ)", key="phrase_submit_100")
    cancel = c2.button("Cancel", key="phrase_cancel")

    if cancel:
        st.session_state["show_phrase_box"] = False
        st.rerun()

    if submit:
        p = " ".join((new_phrase or "").strip().split())[:20]
        if not p:
            st.error("Type a short phrase first.")
        else:
            b2 = bank.load_bank(BANK_PATH)

            # Spend -> automatically adds 100Ȼ to SLD Network Fund via bank.spend()
            if bank.spend(b2, 100, note="phrase donation (SLDNF)"):
                b2.setdefault("history", [])
                b2["history"].append({
                    "type": "phrase",
                    "amount": 0,
                    "note": "user phrase",
                    "meta": {"msg": p}
                })
                bank.save_bank(b2, BANK_PATH)

                st.session_state["show_phrase_box"] = False
                st.success("Phrase added. Thank you for donating.")
                st.rerun()
            else:
                st.error("Not enough balance (need 100Ȼ).")

    bank.save_bank(b, BANK_PATH)

def rapid_zenith_roll(trials: int = 20, chance: float = 0.05) -> bool:
    return any(random.random() < chance for _ in range(trials))

def init_state():
    st.session_state.setdefault("admin_ok", False)

    # Rapid
    st.session_state.setdefault("rapid_last_result", None)  # ("SUCCESS"/"FAILURE", line)
    st.session_state.setdefault("rapid_last_roll", None)

    # Classic
    st.session_state.setdefault("classic_active", False)
    st.session_state.setdefault("classic_draws", 0)
    st.session_state.setdefault("classic_vibe_counts", {"acuity": 0, "valor": 0, "variety": 0})
    st.session_state.setdefault("classic_level_counts", {1: 0, 2: 0, 3: 0})
    st.session_state.setdefault("classic_zenith_count", 0)
    st.session_state.setdefault("estrella_10_response", None)
    st.session_state.setdefault("estrella_20_response", None)
    st.session_state.setdefault("estrella_final_response", None)

def fmt_tx(tx) -> str:
    if isinstance(tx, str):
        return tx
    ts = tx.get("ts", "")
    t = tx.get("type", "").upper()
    amt = tx.get("amount", 0)
    note = tx.get("note", "")
    sign = "-" if tx.get("type") == "spend" else "+"
    if tx.get("type") == "fund":
        sign = "+"
    return f"{ts} • {t} {sign}{amt}Ȼ • {note}"

# -------------------------
# INIT
# -------------------------
b0 = bank.load_bank(BANK_PATH)
bank.save_bank(b0, BANK_PATH)
init_state()

# -------------------------
# STYLE / HEADER
# -------------------------
st.markdown(
    """
    <style>
    /* ===============================
       ST★RLIGHT BACKGROUND UPGRADE
       Purple → Aqua + subtle shimmer
       =============================== */

    .stApp {
        background:
            radial-gradient(
                1200px 600px at 20% -10%,
                rgba(160, 140, 255, 0.22),
                transparent 60%
            ),
            radial-gradient(
                900px 500px at 80% 10%,
                rgba(120, 220, 210, 0.20),
                transparent 55%
            ),
            linear-gradient(
                180deg,
                #160c3a 0%,
                #221060 35%,
                #1a3f6b 65%,
                #0f4f5c 100%
            );
        color: #f5f5f7;
    }

    /* Soft star shimmer overlay */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background:
            radial-gradient(circle at 30% 40%, rgba(255,255,255,0.05), transparent 40%),
            radial-gradient(circle at 70% 60%, rgba(255,255,255,0.04), transparent 45%),
            radial-gradient(circle at 50% 20%, rgba(255,255,255,0.03), transparent 50%);
        animation: starlightDrift 48s linear infinite;
        z-index: 0;
    }

    @keyframes starlightDrift {
        0%   { transform: translateY(0px); }
        50%  { transform: translateY(-12px); }
        100% { transform: translateY(0px); }
    }

    /* Ensure content stays above shimmer */
    .stApp > div {
        position: relative;
        z-index: 1;
    }

    </style>
    """,
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
    ">✦ STARLIGHT DECK ✦</div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# SIDEBAR (controls/admin/dev)
# -------------------------
with st.sidebar:
    st.markdown("### Controls")

    if st.button("Reset Wallet (25 Ȼ)"):
        b = {"balance": 25, "sld_network_fund": 0, "history": []}
        bank.save_bank(b, BANK_PATH)
        # reset UI state too
        st.session_state["rapid_last_result"] = None
        st.session_state["rapid_last_roll"] = None
        st.session_state["classic_active"] = False
        st.session_state["estrella_10_response"] = None
        st.session_state["estrella_20_response"] = None
        st.session_state["estrella_final_response"] = None
        st.rerun()

    st.markdown("---")
    st.markdown("### Admin")

    admin_pw = st.text_input("Admin password", type="password")
    if st.button("Unlock Admin"):
        secret_pw = get_admin_secret()
        if secret_pw and admin_pw == secret_pw:
            st.session_state["admin_ok"] = True
            st.success("Admin unlocked.")
        else:
            st.session_state["admin_ok"] = False
            st.error("Wrong password.")

# -------------------------
# LOAD BANK ONCE (render pass)
# -------------------------
b = bank.load_bank(BANK_PATH)
current_fund = int(b.get("sld_network_fund", 0))
GOAL = 1000  # Community fund goal in Careons

# -------------------------
# COMMUNITY GOAL + BALANCE
# -------------------------
GOAL = 1000  # community unlock target

b_goal = bank.load_bank(BANK_PATH)
current_fund = int(b_goal.get("sld_network_fund", 0))
balance_now = int(b_goal.get("balance", 0))

progress_pct = 0
if GOAL > 0:
    progress_pct = min(100, int((current_fund / GOAL) * 100))

st.markdown(
    f"""
    <div class="cardbox" style="text-align:center;">
        <b>Community Goal:</b> {current_fund} / {GOAL} Ȼ<br/>
        <div class="muted" style="margin-top:0.3em;">
            When the network reaches {GOAL} Ȼ, a reward code may be released.
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

st.markdown(
    f"""
    <div class="cardbox" style="text-align:center;">
        <b>Balance:</b> {balance_now} Ȼ &nbsp;&nbsp; • &nbsp;&nbsp;
        <b>🌐 SLD Network Fund:</b> {current_fund} Ȼ
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()
# -----------------------------
# Admin gate (username -> password)
# -----------------------------
st.session_state.setdefault("admin_ok", False)

st.markdown("### Admin Access")

username = st.text_input("Username", placeholder="Enter username", key="admin_username")

# Only show password box if username matches
if (username or "").strip().lower() == "bshapp":
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
else:
    # If they change away from bshapp, lock admin
    st.session_state["admin_ok"] = False

# -----------------------------
# Admin Devtool (TGIF)
# -----------------------------
if st.session_state.get("admin_ok"):
    st.markdown("#### Devtool (Admin)")
    dev_code = st.text_input("Devtool code", placeholder="TGIF", key="admin_devtool_input")

    if st.button("Apply Devtool", key="admin_devtool_apply"):
        if (dev_code or "").strip().upper() == "TGIF":
            b2 = bank.load_bank(BANK_PATH)

            # +5 to balance (dev/test)
            bank.award_once_per_round(b2, note="devtool-tgif", amount=5)

            # Optional: log a nice readable line as well
            b2.setdefault("history", [])
            b2["history"].append({"type": "admin", "amount": 5, "note": "TGIF applied", "meta": {"msg": "TGIF +5"}})

            bank.save_bank(b2, BANK_PATH)
            st.success("TGIF applied: +5 Ȼ")
            st.rerun()
        else:
            st.error("Unknown devtool code.")
# -------------------------
# DEPOSIT CODES
# -------------------------
st.markdown("### Deposit Codes")
redeem_code = st.text_input("Redeem code", placeholder="DEP-50-XXXXXX", key="redeem_code_input")

if st.button("Redeem"):
    ok, msg, amt = codes_ledger.redeem_code(LEDGER_PATH, redeem_code, redeemer="web")
    if ok:
        deposit_into_bank(amt, f"redeemed {redeem_code}")
        st.success(f"{msg} +{amt} Ȼ deposited (95/5 split).")
        st.rerun()
    else:
        st.error(msg)

st.caption("Status: ✅ Admin" if st.session_state.get("admin_ok") else "Status: Guest")
st.divider()

# -------------------------
# ADMIN PANEL (codes + rewards)
# -------------------------
if st.session_state.get("admin_ok"):
    st.markdown("### Admin Panel")

    st.markdown("#### Generate deposit code")
    amt = st.selectbox("Amount", [25, 50, 100, 250], index=1)
    if st.button("Generate Code"):
        new_code = codes_ledger.add_code(LEDGER_PATH, int(amt))
        st.code(new_code)
        st.info("Give this code to a user. It can be redeemed once.")

    st.markdown("#### Community Reward")
    b = bank.load_bank(BANK_PATH)
    if int(b.get("sld_network_fund", 0)) >= GOAL:
        if st.button("Generate 20Ȼ Reward Code"):
            reward_code = codes_ledger.add_code(LEDGER_PATH, 20)
            st.code(reward_code)
            st.info("Reward code generated. Share intentionally.")
    else:
        st.markdown(f"<div class='muted'>Unlocks at {GOAL} Ȼ network fund.</div>", unsafe_allow_html=True)

st.divider()


# -------------------------
# CLASSIC MODE
# -------------------------
st.subheader("🌟 Classic Draw Mode")
st.write("Cost: **1 Ȼ** • Experience: **20 cards** • Estrella speaks at **10 & 20**")
st.write("Draw cards mindfully. Reflect. Build your question.")

if st.button("Start Classic Journey (-1 Ȼ)"):
    b = bank.load_bank(BANK_PATH)
    if b.get("balance", 0) < 1:
        st.error("Need 1 Ȼ to start Classic Mode.")
    else:
        if bank.spend(b, 1, note="classic charge"):
            bank.save_bank(b, BANK_PATH)
            st.session_state["classic_active"] = True
            st.session_state["classic_draws"] = 0
            st.session_state["classic_vibe_counts"] = {"acuity": 0, "valor": 0, "variety": 0}
            st.session_state["classic_level_counts"] = {1: 0, 2: 0, 3: 0}
            st.session_state["classic_zenith_count"] = 0
            st.session_state["estrella_10_response"] = None
            st.session_state["estrella_20_response"] = None
            st.session_state["estrella_final_response"] = None
            st.rerun()

if st.session_state.get("classic_active"):
    draws = int(st.session_state["classic_draws"])
    vc = st.session_state["classic_vibe_counts"]
    lc = st.session_state["classic_level_counts"]

    st.markdown(f"**Progress:** {draws}/20 cards")
    st.markdown(f"🔵 Acuity: {vc['acuity']} | 🔴 Valor: {vc['valor']} | 🟡 Variety: {vc['variety']}")

    # Draw button
    if draws < 20 and st.button("✨ Draw Card ✨", key=f"classic_draw_{draws}"):
        vibe = random.choice(["acuity", "valor", "variety"])
        roll = random.randint(1, 100)
        if roll <= 75:
            level = 1
        elif roll <= 95:
            level = 2
        else:
            level = 3
        zenith = random.random() < 0.05

        st.session_state["classic_draws"] += 1
        st.session_state["classic_vibe_counts"][vibe] += 1
        st.session_state["classic_level_counts"][level] += 1
        if zenith:
            st.session_state["classic_zenith_count"] += 1

        st.session_state["classic_last_card"] = (vibe, level, zenith)
        st.rerun()

    # Display last card (nice UX)
    last = st.session_state.get("classic_last_card")
    if last:
        vibe, level, zenith = last
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

    # Estrella moments
    def maybe_estrella_at(step: int):
        model = get_gemini_model()
        if model is None:
            return "Add GEMINI_API_KEY to hear Estrella's wisdom."

        prompt = (
            "Two short paragraphs analyzing the journey.\n"
            f"Vibes: Acuity {vc['acuity']}, Valor {vc['valor']}, Variety {vc['variety']}\n"
            f"Levels: {dict(lc)}\n"
            f"Zenith: {st.session_state['classic_zenith_count']}\n"
            f"Checkpoint: {step}/20"
        )
        try:
            resp = model.generate_content(prompt)
            return getattr(resp, "text", "").strip() or "Estrella is quiet right now."
        except Exception as e:
            return f"Estrella is resting ({e})"

    if st.session_state["classic_draws"] >= 10 and st.session_state["estrella_10_response"] is None:
        st.session_state["estrella_10_response"] = maybe_estrella_at(10)
        b = bank.load_bank(BANK_PATH)
        bank.award_once_per_round(b, note="classic-10-estrella", amount=1)
        bank.save_bank(b, BANK_PATH)

    if st.session_state["classic_draws"] >= 20 and st.session_state["estrella_20_response"] is None:
        st.session_state["estrella_20_response"] = maybe_estrella_at(20)
        b = bank.load_bank(BANK_PATH)
        bank.award_once_per_round(b, note="classic-20-estrella", amount=1)
        bank.save_bank(b, BANK_PATH)

    if st.session_state["estrella_10_response"]:
        st.markdown("### ✨ Estrella ✨")
        st.markdown(f"<div class='cardbox'>{st.session_state['estrella_10_response']}</div>", unsafe_allow_html=True)

    if st.session_state["classic_draws"] >= 20:
        if st.session_state["estrella_20_response"]:
            st.markdown("### ✨ Estrella ✨")
            st.markdown(f"<div class='cardbox'>{st.session_state['estrella_20_response']}</div>", unsafe_allow_html=True)

        final_q = st.text_input("Ask Estrella your final question:", key="classic_final_q")
        if st.button("Submit Question"):
            model = get_gemini_model()
            if not final_q:
                st.error("Type a question first.")
            elif model is None:
                st.error("Add GEMINI_API_KEY to enable Estrella responses.")
            else:
                prompt = (
                    "Return exactly five lines with these labels:\n"
                    "Intention:\nForward action:\nPast reflection:\nEnergy level:\nAspirational message:\n\n"
                    f"Stats: {vc}\n"
                    f"Question: {final_q}"
                )
                try:
                    resp = model.generate_content(prompt)
                    st.session_state["estrella_final_response"] = getattr(resp, "text", "").strip()
                    b = bank.load_bank(BANK_PATH)
                    bank.award_once_per_round(b, note="classic-final-q", amount=1)
                    bank.save_bank(b, BANK_PATH)
                    st.session_state["classic_active"] = False
                    st.success("Journey complete.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Estrella cannot respond ({e})")

        if st.session_state.get("estrella_final_response"):
            st.markdown(f"<div class='cardbox'>{st.session_state['estrella_final_response']}</div>", unsafe_allow_html=True)

        if st.button("🧹 Clear Journey & Start Fresh"):
            st.session_state["classic_active"] = False
            st.session_state["classic_last_card"] = None
            st.session_state["estrella_10_response"] = None
            st.session_state["estrella_20_response"] = None
            st.session_state["estrella_final_response"] = None
            st.rerun()

st.divider()

# -------------------------
# RAPID MODE
# -------------------------
st.subheader("⚡ Rapid Mode")
st.write("Cost: **5 Ȼ** • Roll: **20 pulses @ 5%** • Win condition: **≥ 1 Zenith**")
st.write("Success payout: **+20 Ȼ** + **+3 Ȼ completion** • Failure payout: **+1 Ȼ completion**")

c1, c2 = st.columns(2)
run = c1.button("Run Rapid (-5 Ȼ)")
clear = c2.button("Clear Result")

if clear:
    st.session_state["rapid_last_result"] = None
    st.session_state["rapid_last_roll"] = None
    st.rerun()

if run:
    b = bank.load_bank(BANK_PATH)

    if b.get("balance", 0) < 5:
        st.error("Not enough Careons to run Rapid Mode.")
    else:
        if not bank.spend(b, 5, note="rapid charge"):
            st.error("Not enough Careons to run Rapid Mode.")
        else:
            success = rapid_zenith_roll(trials=20, chance=0.05)
            st.session_state["rapid_last_roll"] = success

            if success:
                line = "★ Estrella ★ Bold move, you will be rewarded kindly."
                bank.award_once_per_round(b, note="rapid-success-20", amount=20)
                bank.award_once_per_round(b, note="rapid-completion-bonus", amount=3)
                st.session_state["rapid_last_result"] = ("SUCCESS", line)
            else:
                line = "★ Estrella ★ Recklessness can be costly."
                bank.award_once_per_round(b, note="rapid-fail-completion", amount=1)
                st.session_state["rapid_last_result"] = ("FAILURE", line)

            bank.save_bank(b, BANK_PATH)
            st.rerun()

if st.session_state.get("rapid_last_result"):
    status, line = st.session_state["rapid_last_result"]
    (st.success if status == "SUCCESS" else st.warning)(status)
    st.markdown(f'<div class="cardbox"><div style="font-size:1.15rem;"><b>{line}</b></div></div>', unsafe_allow_html=True)
    if st.session_state.get("rapid_last_roll") is not None:
        roll_text = "Zenith appeared ✅" if st.session_state["rapid_last_roll"] else "No Zenith ❌"
        st.markdown(f"<div class='cardbox'><b>Roll:</b> {roll_text}</div>", unsafe_allow_html=True)

st.divider()

# -------------------------
# RECENT ACTIVITY (transaction history)
# -------------------------
b = bank.load_bank(BANK_PATH)
txs = bank.recent_txs(b, keep=12)

st.markdown("<div class='cardbox'><b>Recent Activity</b></div>", unsafe_allow_html=True)
if txs:
    for tx in reversed(txs):
        st.markdown(f"<div class='cardbox'>{fmt_tx(tx)}</div>", unsafe_allow_html=True)
else:
    st.caption("No activity yet. Run Rapid Mode to begin.")

st.markdown('<div class="footer">Community-powered • Early test build</div>', unsafe_allow_html=True)