import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client
# It will automatically read the OPENAI_API_KEY from the Streamlit "Secrets"
try:
    client = OpenAI()
except Exception as e:
    st.error("Failed to initialize OpenAI client. Have you set your OPENAI_API_KEY in the Streamlit secrets?")
    st.stop()

# --- App Title ---
st.title("My Prompt Test App 💬")
st.write("Using prompt: pmpt_690069ca73ac8190a17467e9d9850aec0f5728a89768fdc9") # Make sure this ID is still correct

# --- Session State for Memory ---
# This is how we store the conversation_id and message history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None # Start with no conversation ID

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input Box ---
if user_input := st.chat_input("What is up?"): # Changed variable name for clarity

    # 1. Add user's message to UI and history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Call the OpenAI Prompts API with the CORRECTED structure
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # --- THIS CALL USES THE CORRECT STRUCTURE ---
                response = client.responses.create(
                    prompt={
                        "id": "pmpt_690069ca73ac8190a17467e9d9850aec0f5728a89768fdc9", # Use your prompt ID
                        "version": "8",  # Use the latest published version
                        "variables": {
                            "user_message": user_input,
                            # conversation_id is passed as a top-level argument below for API memory,
                            # it doesn't need to be in 'variables' unless your prompt *text* uses {{conversation_id}}
                        }
                    },
                    # The conversation_id for the API's memory tracking is a top-level argument
                    conversation_id=st.session_state.conversation_id
                )
                # --- END OF CORRECTED CALL ---

                # Get the text response
                assistant_response = response.text

                # IMPORTANT: Save the new conversation_id returned by the API for the next turn
                st.session_state.conversation_id = response.conversation_id

                # Display and save the response
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error("Please double-check your prompt ID, version, variable names in the prompt config, and ensure the OpenAI library is up-to-date in requirements.txt (e.g., openai>=1.0.0).")
