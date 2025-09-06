import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt

# ==============================
# Default API Key (replace if needed)
# ==============================
DEFAULT_API_KEY = "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"

# Fallback model order
MODEL_PRIORITY = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

# ==============================
# Streamlit App Config
# ==============================
st.set_page_config(
    page_title="Cohort 2 Ask !! Me",
    page_icon="💬",
    layout="wide"
)

# Title
st.title("💬 Cohort 2  Ask !! Me")
st.markdown("Your personal AI assistant with model fallback and live usage stats 📊")

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
    # Session State for Chat + Stats
    # ==============================
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "token_usage" not in st.session_state:
        st.session_state.token_usage = []  # tokens per response

    # ==============================
    # Layout: Two Columns (Chat | Stats)
    # ==============================
    chat_col, stats_col = st.columns([2, 1])

    # ------------------
    # Chat Column
    # ------------------
    with chat_col:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            response_text, total_tokens = None, 0

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
                    if i > 0:  # means fallback happened
                        st.warning(f"⚠️ The model **{MODEL_PRIORITY[i-1]}** is exhausted. Switching to **{model}**.")
                    break
                except Exception as e:
                    st.warning(f"⚠️ Model **{model}** failed: {e}")
                    continue

            if response_text:
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.session_state.token_usage.append(total_tokens)

                with st.chat_message("assistant"):
                    st.markdown(response_text)
            else:
                st.error("❌ All models failed. Please check your API key or quota.")

    # ------------------
    # Stats Column
    # ------------------
    with stats_col:
        st.subheader("📊 API Usage Stats")

        if st.session_state.token_usage:
            total = sum(st.session_state.token_usage)
            avg = total / len(st.session_state.token_usage)
            st.metric("🔢 Total Tokens Used", total)
            st.metric("📈 Avg Tokens per Response", round(avg, 2))
            st.metric("💬 Messages Sent", len(st.session_state.messages))

            # Token usage graph
            fig, ax = plt.subplots()
            ax.plot(
                range(1, len(st.session_state.token_usage) + 1),
                st.session_state.token_usage,
                marker="o", linestyle="-", color="b"
            )
            ax.set_title("Token Usage per Response")
            ax.set_xlabel("Response #")
            ax.set_ylabel("Tokens Used")
            st.pyplot(fig)
        else:
            st.info("No token stats yet. Start chatting to see usage!")
