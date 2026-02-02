import os
import random
from datetime import datetime

import streamlit as st

import careon_bank_v2 as bank
import ui_header
import careon_bubble
import careon_market
import codes_ledger


# -------------------------
# PAGE CONFIG (must be first Streamlit call)
# -------------------------
st.set_page_config(page_title="Starlight Deck", layout="centered")


# -------------------------
# PATHS
# -------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "careon_bank_v2.json")
LEDGER_PATH = os.path.join(HERE, "codes_ledger.json")


# -------------------------
# CONSTANTS
# -------------------------
GOAL = 1000
MODEL_NAME = "gemini-2.0-flash"


# -------------------------
# ENSURE BANK FILE EXISTS
# -------------------------
b_init = bank.load_bank(BANK_PATH)
bank.save_bank(b_init, BANK_PATH)


# -------------------------
# SESSION STATE DEFAULTS
# -------------------------
st.session_state.setdefault("show_market", False)
st.session_state.setdefault("admin_ok", False)

st.session_state.setdefault("show_phrase_box", False)

# Rapid
st.session_state.setdefault("rapid_last_result", None)  # ("SUCCESS"/"FAILURE", line)
st.session_state.setdefault("rapid_last_roll", None)

# Classic
st.session_state.setdefault("classic_active", False)
st.session_state.setdefault("classic_draws", 0)
st.session_state.setdefault("classic_vibe_counts", {"acuity": 0, "valor": 0, "variety": 0})
st.session_state.setdefault("classic_level_counts", {1: 0, 2: 0, 3: 0})
st.session_state.setdefault("classic_zenith_count", 0)
st.session_state.setdefault("classic_last_card", None)
st.session_state.setdefault("estrella_10_response", None)
st.session_state.setdefault("estrella_20_response", None)
st.session_state.setdefault("estrella_final_response", None)

st.session_state.setdefault("username", "")
st.session_state.setdefault("admin_ok", False)
# -------------------------
# GEMINI (Estrella) — Flash Demo
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


def gemini_ready() -> bool:
    return GENAI_AVAILABLE and bool(GEMINI_API_KEY)


def get_gemini_model():
    if not gemini_ready():
        return None
    try:
        return genai.GenerativeModel(MODEL_NAME)
    except Exception:
        return None


# -------------------------
# HELPERS
# -------------------------
def now_z() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def get_admin_secret() -> str | None:
    try:
        pw = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        pw = None
    if not pw:
        pw = os.getenv("SLD_ADMIN_PASSWORD")
    return pw


def recent_txs(b: dict, keep: int = 12) -> list:
    """Bank history is a list; return last `keep` entries safely."""
    hist = b.get("history", []) or []
    if not isinstance(hist, list):
        return []
    return hist[-keep:]


def fmt_tx(tx) -> str:
    """Readable history line for dict tx objects."""
    if isinstance(tx, str):
        return tx
    if not isinstance(tx, dict):
        return str(tx)
    ts = tx.get("ts", "")
    t = (tx.get("type") or "").upper()
    amt = tx.get("amount", 0)
    note = tx.get("note", "")
    sign = "-" if tx.get("type") == "spend" else "+"
    return f"{ts} • {t} {sign}{amt}Ȼ • {note}"


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
    b["balance"] = int(b.get("balance", 0)) + user_amount
    b["sld_network_fund"] = int(b.get("sld_network_fund", 0)) + network_cut

    b.setdefault("history", [])
    b["history"].append({"ts": now_z(), "type": "fund", "amount": network_cut, "note": f"{note} (network)"})
    b["history"].append({"ts": now_z(), "type": "earn", "amount": user_amount, "note": f"{note} (user)"})

    bank.save_bank(b, BANK_PATH)


def rapid_zenith_roll(trials: int = 20, chance: float = 0.05) -> bool:
    return any(random.random() < chance for _ in range(trials))


# -------------------------
# BUILD TICKER PHRASES (from bank history)
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
    if len(phrases) >= 12:
        break


# -------------------------
# TOP UI (render ONCE)
# -------------------------
import audio_ambience
import vip_status

ui_header.render_header(ticker_items=phrases)
careon_bubble.render_bubble()
careon_market.render_market(bank, BANK_PATH)

# Audio controls (floating bottom-right)
audio_ambience.render_audio_controls()

st.divider()

# VIP Status Badge (after username section, around line 220)
# Replace the username section with:
name = st.text_input(
    "Username",
    value=st.session_state.get("username", ""),
    placeholder="Type a name (e.g., KingQuantum)",
    max_chars=16,
    key="username_input"
).strip()

st.session_state["username"] = name

# Show VIP badge
b_for_vip = bank.load_bank(BANK_PATH)
vip_status.render_vip_badge(b_for_vip.get("balance", 0), name)

# Auto-admin if username matches
if name.lower() in {"bshappy", "bshapp"}:
    st.session_state["admin_ok"] = True
    st.caption("Status: ✅ Admin")
else:
    st.session_state["admin_ok"] = False

# -------------------------
# COMMUNITY GOAL + BALANCE (clean, single instance)
# -------------------------
b_goal = bank.load_bank(BANK_PATH)
current_fund = int(b_goal.get("sld_network_fund", 0) or 0)
balance_now = int(b_goal.get("balance", 0) or 0)

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


# -------------------------
# SIDEBAR (admin + TGIF)
# -------------------------
with st.sidebar:
    st.markdown("### Admin Access")

    username = st.text_input("Username", placeholder="Enter username", key="admin_username")

    if (username or "").strip().lower() == "bshapp":
        admin_pw = st.text_input("Admin password", type="password", key="admin_pw_input")
        if st.button("Unlock Admin", key="admin_unlock_btn"):
            secret_pw = get_admin_secret()
            if secret_pw and admin_pw == secret_pw:
                st.session_state["admin_ok"] = True
                st.success("Admin unlocked.")
                st.rerun()
            else:
                st.session_state["admin_ok"] = False
                st.error("Wrong password.")
    else:
        st.session_state["admin_ok"] = False

    if st.session_state.get("admin_ok"):
        st.markdown("---")
        st.markdown("### Devtool")
        dev_code = st.text_input("Devtool code", placeholder="TGIF", key="admin_devtool_input")

        if st.button("Apply Devtool", key="admin_devtool_apply"):
            if (dev_code or "").strip().upper() == "TGIF":
                b2 = bank.load_bank(BANK_PATH)
                bank.award_once_per_round(b2, note="devtool-tgif", amount=5)
                b2.setdefault("history", [])
                b2["history"].append({"ts": now_z(), "type": "admin", "amount": 5, "note": "TGIF applied"})
                bank.save_bank(b2, BANK_PATH)
                st.success("TGIF applied: +5 Ȼ")
                st.rerun()
            else:
                st.error("Unknown devtool code.")


# -------------------------
# DONATE → SUBMIT PHRASE (100Ȼ)
# -------------------------
st.markdown("### Community Phrase")

if st.button("🤝 Donate to the community (SLDNF)", key="btn_donate_open"):
    st.session_state["show_phrase_box"] = True

if st.session_state.get("show_phrase_box"):
    st.caption("Max 20 characters • Costs 100Ȼ • Donation funds SLD Network Fund (SLDNF).")

    new_phrase = st.text_input("Your phrase", max_chars=20, key="phrase_add_input")
    user_for_phrase = st.text_input(
    "Name (optional)",
    value=st.session_state.get("username", ""),
    max_chars=16,
    key="phrase_user_input"
)

    c1, c2 = st.columns(2)
    submit = c1.button("Submit Phrase (-100Ȼ)", key="phrase_submit_100")
    cancel = c2.button("Cancel", key="phrase_cancel")

    if cancel:
        st.session_state["show_phrase_box"] = False
        st.rerun()

    if submit:
        p = " ".join((new_phrase or "").strip().split())[:20]
        u = " ".join((user_for_phrase or "").strip().split())[:16]
        if not p:
            st.error("Type a short phrase first.")
        else:
            b2 = bank.load_bank(BANK_PATH)
            if bank.spend(b2, 100, note="phrase donation (SLDNF)"):
                b2.setdefault("history", [])
                b2["history"].append({
                    "ts": now_z(),
                    "type": "phrase",
                    "amount": 0,
                    "note": "user phrase",
                    "meta": {"msg": p, "user": u}
                })
                bank.save_bank(b2, BANK_PATH)
                st.session_state["show_phrase_box"] = False
                st.success("Phrase added. Thank you for donating.")
                st.rerun()
            else:
                st.error("Not enough balance (need 100Ȼ).")

st.divider()


# -------------------------
# DEPOSIT CODES
# -------------------------
st.markdown("### Deposit Codes")
redeem_code = st.text_input("Redeem code", placeholder="DEP-50-XXXXXX", key="redeem_code_input")

if st.button("Redeem", key="redeem_btn"):
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
    amt = st.selectbox("Amount", [25, 50, 100, 250], index=1, key="gen_amt")
    if st.button("Generate Code", key="gen_code_btn"):
        new_code = codes_ledger.add_code(LEDGER_PATH, int(amt))
        st.code(new_code)
        st.info("Give this code to a user. It can be redeemed once.")

    st.markdown("#### Community Reward")
    b_check = bank.load_bank(BANK_PATH)
    if int(b_check.get("sld_network_fund", 0)) >= GOAL:
        if st.button("Generate 20Ȼ Reward Code", key="gen_reward_btn"):
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

if st.button("Start Classic Journey (-1 Ȼ)", key="classic_start_btn"):
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
            st.session_state["classic_last_card"] = None
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

    if draws < 20 and st.button("✨ Draw Card ✨", key=f"classic_draw_{draws}"):
        vibe = random.choice(["acuity", "valor", "variety"])
        roll = random.randint(1, 100)
        level = 1 if roll <= 75 else (2 if roll <= 95 else 3)
        zenith = random.random() < 0.05

        st.session_state["classic_draws"] += 1
        st.session_state["classic_vibe_counts"][vibe] += 1
        st.session_state["classic_level_counts"][level] += 1
        if zenith:
            st.session_state["classic_zenith_count"] += 1

        st.session_state["classic_last_card"] = (vibe, level, zenith)
        st.rerun()

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

    def estrella_checkpoint(step: int) -> str:
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
        st.session_state["estrella_10_response"] = estrella_checkpoint(10)
        b_aw = bank.load_bank(BANK_PATH)
        bank.award_once_per_round(b_aw, note="classic-10-estrella", amount=1)
        bank.save_bank(b_aw, BANK_PATH)

    if st.session_state["classic_draws"] >= 20 and st.session_state["estrella_20_response"] is None:
        st.session_state["estrella_20_response"] = estrella_checkpoint(20)
        b_aw = bank.load_bank(BANK_PATH)
        bank.award_once_per_round(b_aw, note="classic-20-estrella", amount=1)
        bank.save_bank(b_aw, BANK_PATH)

    if st.session_state.get("estrella_10_response"):
        st.markdown("### ✨ Estrella ✨")
        st.markdown(f"<div class='cardbox'>{st.session_state['estrella_10_response']}</div>", unsafe_allow_html=True)

    if st.session_state["classic_draws"] >= 20:
        if st.session_state.get("estrella_20_response"):
            st.markdown("### ✨ Estrella ✨")
            st.markdown(f"<div class='cardbox'>{st.session_state['estrella_20_response']}</div>", unsafe_allow_html=True)

        final_q = st.text_input("Ask Estrella your final question:", key="classic_final_q")
        if st.button("Submit Question", key="classic_submit_q"):
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
                    b_aw = bank.load_bank(BANK_PATH)
                    bank.award_once_per_round(b_aw, note="classic-final-q", amount=1)
                    bank.save_bank(b_aw, BANK_PATH)
                    st.session_state["classic_active"] = False
                    st.success("Journey complete.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Estrella cannot respond ({e})")

        if st.session_state.get("estrella_final_response"):
            st.markdown(f"<div class='cardbox'>{st.session_state['estrella_final_response']}</div>", unsafe_allow_html=True)

        if st.button("🧹 Clear Journey & Start Fresh", key="classic_clear_btn"):
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
run = c1.button("Run Rapid (-5 Ȼ)", key="rapid_run_btn")
clear = c2.button("Clear Result", key="rapid_clear_btn")

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
# RECENT ACTIVITY
# -------------------------
b_hist = bank.load_bank(BANK_PATH)
txs = recent_txs(b_hist, keep=12)

st.markdown("<div class='cardbox'><b>Recent Activity</b></div>", unsafe_allow_html=True)
if txs:
    for tx in reversed(txs):
        st.markdown(f"<div class='cardbox'>{fmt_tx(tx)}</div>", unsafe_allow_html=True)
else:
    st.caption("No activity yet. Run Rapid Mode to begin.")

st.markdown('<div class="footer">Community-powered • Early test build</div>', unsafe_allow_html=True)