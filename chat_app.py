import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt

# Fallback models in priority order
MODEL_PRIORITY = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

# Streamlit page config
st.set_page_config(
    page_title="Cohort 2 Ask !! Me",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Cohort 2 Ask !! Me")
st.markdown("🚀 Chat with fallback API keys.")

# Password-masked API keys input
api_keys_input = st.text_input(
    "🔑 Enter OpenAI API Keys (comma separated, fallback order):",
    type="password",
    placeholder="sk-xxxxxxxx1, sk-xxxxxxxx2"
)

api_keys = [key.strip() for key in api_keys_input.split(",") if key.strip()]

if not api_keys:
    st.error("❌ Provide at least one valid OpenAI API key to continue.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "token_usage" not in st.session_state:
        st.session_state.token_usage = []

    if "api_key_used" not in st.session_state:
        st.session_state.api_key_used = []

    chat_col, stats_col = st.columns([2, 1])

    # ---------------- Chat Column ----------------
    with chat_col:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            response_text, total_tokens = None, 0
            key_tried = None

            for api_key in api_keys:
                key_tried = api_key
                client = OpenAI(api_key=api_key)

                for model in MODEL_PRIORITY:
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            messages=st.session_state.messages
                        )
                        response_text = response.choices[0].message.content
                        total_tokens = (
                            response.usage.total_tokens if hasattr(response, "usage") else 0
                        )
                        st.session_state.api_key_used.append(key_tried)
                        if model != MODEL_PRIORITY[0]:
                            st.info(f"⚠️ Fallback model used: {model}")
                        break  # Success

                    except Exception as e:
                        err_msg = str(e).lower()
                        if "401" in err_msg or "invalid api key" in err_msg:
                            st.warning(f"🚫 Invalid API Key tried: {key_tried}")
                            break
                        elif "429" in err_msg or "quota" in err_msg:
                            st.warning(f"🚧 Quota exhausted for key: {key_tried}, trying next key...")
                            continue
                        else:
                            st.warning(f"⚠️ Model {model} failed: {e}")
                            continue

                if response_text:
                    break

            if response_text:
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.session_state.token_usage.append(total_tokens)

                with st.chat_message("assistant"):
                    st.markdown(response_text)
            else:
                st.error("❌ All API keys and models exhausted. Please check your keys or usage.")

    # ---------------- Stats Column ----------------
    with stats_col:
        st.subheader("📊 API & Token Metrics")

        if st.session_state.token_usage:
            total_tokens = sum(st.session_state.token_usage)
            avg_tokens = total_tokens / len(st.session_state.token_usage)
            st.metric("💡 Total Tokens Used", total_tokens)
            st.metric("📈 Avg Tokens per Response", round(avg_tokens, 2))
            st.metric("🔑 Unique API Keys Used", len(set(st.session_state.api_key_used)))
            st.metric("💬 Messages Sent", len(st.session_state.messages))

            # Burndown Graph: Token Usage Per Response
            fig, ax = plt.subplots(figsize=(6, 4), facecolor="#0E1117")
            ax.set_facecolor("#1A1D23")
            ax.plot(
                range(1, len(st.session_state.token_usage) + 1),
                st.session_state.token_usage,
                marker="o", linestyle="-", color="#1DB954"
            )
            ax.set_title("Token Usage Per Response", color="white", fontsize=14)
            ax.set_xlabel("Response #", color="white")
            ax.set_ylabel("Tokens Used", color="white")
            ax.tick_params(colors="white")
            st.pyplot(fig, clear_figure=True)
        else:
            st.info("📊 API & Token metrics will appear after your first interaction.")
