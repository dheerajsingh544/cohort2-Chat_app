import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt

# ==============================
# Default API Key (leave empty for security, force user input)
# ==============================
DEFAULT_API_KEY = "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"

# Model fallback order
MODEL_PRIORITY = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

# ==============================
# Streamlit Config
# ==============================
st.set_page_config(
    page_title="Cohort 2 Ask !! Me",
    page_icon="💬",
    layout="wide"
)

# Title
st.title("💬 Cohort 2 Ask !! Me")
st.markdown("Personal AI assistant with model fallback, token stats & smart error handling ⚡")

# ==============================
# API Key Handling
# ==============================
user_api_key = st.text_input("🔑 Enter your OpenAI API key", type="password")
api_key = user_api_key if user_api_key else DEFAULT_API_KEY

if not api_key:
    st.error("❌ No API key provided. Please enter your OpenAI API key above to continue.")
else:
    client = OpenAI(api_key=api_key)

    # ==============================
    # Session State
    # ==============================
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "token_usage" not in st.session_state:
        st.session_state.token_usage = []

    # Layout: Chat + Stats
    chat_col, stats_col = st.columns([2, 1])

    # ------------------
    # Chat Column
    # ------------------
    with chat_col:
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            response_text, total_tokens = None, 0
            invalid_key_error = False
            quota_error = False

            # Try models in fallback order
            for i, model in enumerate(MODEL_PRIORITY):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=st.session_state.messages
                    )
                    response_text = response.choices[0].message.content
                    total_tokens = (
                        response.usage.total_tokens if hasattr(response, "usage") else 0
                    )
                    if i > 0:
                        st.warning(f"⚠️ Previous model exhausted. Switching to **{model}**.")
                    break

                except Exception as e:
                    err_msg = str(e).lower()
                    if "401" in err_msg or "invalid api key" in err_msg:
                        invalid
