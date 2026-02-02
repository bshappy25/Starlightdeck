import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st

st.set_page_config(
    page_title="Starlight Deck",
    layout="centered",
)

st.title("✦ Starlight Deck ✦")

st.markdown(
    """
    Welcome to **Starlight Deck**.

    This is an early web test build.
    Core gameplay is being ported carefully.
    """
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.button("Start Normal")

with col2:
    st.button("Start Rapid")

st.caption("Careon Ȼ • Community-powered • Test deployment")