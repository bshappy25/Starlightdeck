import streamlit as st

# ---------- Page config ----------
st.set_page_config(
    page_title="Starlight Deck",
    layout="centered",
)

# ---------- Style ----------
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background: linear-gradient(180deg, #0f1021 0%, #1b1d3a 100%);
        color: #f5f5f7;
    }

    /* Title styling */
    h1 {
        color: #f6c177;
        text-align: center;
        letter-spacing: 0.05em;
    }

    /* Section text */
    p, li, span, div {
        color: #e6e6eb;
        font-size: 1.05rem;
    }

    /* Buttons */
    .stButton > button {
        background-color: #3f44c8;
        color: white;
        border-radius: 12px;
        padding: 0.6em 1.2em;
        border: none;
        font-size: 1.05rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #5a5ff0;
        transform: scale(1.03);
    }

    /* Careon badge */
    .careon {
        display: inline-block;
        padding: 0.35em 0.75em;
        border-radius: 999px;
        background: rgba(246, 193, 119, 0.15);
        color: #f6c177;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    /* Footer */
    .footer {
        text-align: center;
        opacity: 0.75;
        font-size: 0.85rem;
        margin-top: 2em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- UI ----------
st.title("✦ Starlight Deck ✦")

st.markdown(
    """
    A calm, reflective card experience  
    guided by intuition and gentle structure.
    """
)

st.markdown(
    """
    <div style="text-align:center; margin-top:1em;">
        <span class="careon">Careon Ȼ</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.button("Start Normal")

with col2:
    st.button("Start Rapid")

st.markdown(
    """
    <div class="footer">
        Community-powered • Early test build
    </div>
    """,
    unsafe_allow_html=True,
)