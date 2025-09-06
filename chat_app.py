import streamlit as st
from openai import OpenAI, error
import matplotlib.pyplot as plt

# ==============================
# Default API Key (empty by default)
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
st.markdown("Your personal AI assistant with model fallback, token stats & smart error handling ⚡")

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
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            response_text, total_tokens = None, 0
            invalid_key_error = False
            quota_error = False

            # Try models in priority order
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
                    if i > 0:  # fallback happened
                        st.warning(f"⚠️ Previous model exhausted. Switching to **{model}**.")
                    break

                except Exception as e:
                    err_msg = str(e).lower()
                    if "401" in err_msg or "invalid api key" in err_msg:
                        invalid_key_error = True
                        break
                    elif "429" in err_msg or "quota" in err_msg:
                        quota_error = True
                        continue
                    else:
                        st.warning(f"⚠️ Model **{model}** failed: {e}")
                        continue

            # Show appropriate error messages
            if invalid_key_error:
                st.error("❌ Invalid API key. Please check your OpenAI API key.")
            elif quota_error and not response_text:
                st.error("⚠️ API quota exceeded for all models. Please wait or try another key.")
            elif response_text:
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.session_state.token_usage.append(total_tokens)
                with st.chat_message("assistant"):
                    st.markdown(response_text)
            else:
                st.error("❌ All models failed. Check API key or usage.")

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
            fig, ax = plt.subplots(facecolor="#0E1117")
            ax.set_facecolor("#1A1D23")
            ax.plot(
                range(1, len(st.session_state.token_usage) + 1),
                st.session_state.token_usage,
                marker="o", linestyle="-", color="#1DB954"
            )
            ax.set_title("Token Usage per Response", color="white")
            ax.set_xlabel("Response #", color="white")
            ax.set_ylabel("Tokens Used", color="white")
            ax.tick_params(colors="white")
            st.pyplot(fig)
        else:
            st.info("No token stats yet. Start chatting to see usage!")
