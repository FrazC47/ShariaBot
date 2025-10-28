import streamlit as st
from openai import OpenAI
import os

# =========================
# 🔐 Initialize OpenAI Client
# =========================
try:
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("❌ OpenAI API key not found. Please add it to Streamlit secrets or environment variables.")
        st.stop()

    client = OpenAI(api_key=api_key)

except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {e}")
    st.stop()

# =========================
# 🎨 App Title
# =========================
st.title("Buraq Bank Sharia Finance Bot — Test Version")
PROMPT_ID = "pmpt_690069ca73ac8190a17467e9d9850aec0f5728a89768fdc9"
PROMPT_VERSION = "13"  # ✅ Make sure this matches the current published version
st.write(f"Using prompt: `{PROMPT_ID}` (v{PROMPT_VERSION})")

# =========================
# 💾 Conversation Memory
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# =========================
# 🗨️ Display Chat History
# =========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# 💬 Chat Input
# =========================
if user_input := st.chat_input("Type your question about Sharia finance..."):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # =========================
                # 🚀 OpenAI Responses API Call
                # =========================
                response = client.responses.create(
                    prompt={
                        "id": PROMPT_ID,
                        "version": PROMPT_VERSION,
                        "variables": {
                            "user_message": user_input
                        }
                    },
                    conversation=st.session_state.conversation_id
                )

                # ✅ Extract assistant reply text safely
                assistant_response = getattr(response, "output_text", None)
                if not assistant_response:
                    assistant_response = "⚠️ No text output received from model."

                # ✅ Save conversation context if available
                if hasattr(response, "conversation"):
                    st.session_state.conversation_id = response.conversation

                # ✅ Display assistant response
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.info("Please double-check your prompt ID, version, and variable names. "
                        "Also ensure `openai>=1.2.0` is installed and your API key is valid.")
