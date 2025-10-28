import streamlit as st
from openai import OpenAI
import os # Import os to check for API key in environment first

# Initialize the OpenAI client
# Tries to read the key from Streamlit secrets first, then environment variables
try:
    # Attempt to get key from Streamlit secrets if available
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        # Fallback to environment variable if not in secrets
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("OpenAI API key not found. Please add it to your Streamlit secrets or environment variables.")
        st.stop()

    client = OpenAI(api_key=api_key)

except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {e}")
    st.stop()

# --- App Title ---
st.title("My Prompt Test App 💬")
st.write("Using prompt: pmpt_690069ca73ac8190a17467e9d9850aec0f5728a89768fdc9") # Make sure this ID is still correct

# --- Session State for Memory ---
# This is how we store the conversation ID and message history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None # Start with no conversation ID

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input Box ---
if user_input := st.chat_input("What is up?"):

    # 1. Add user's message to UI and history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Call the OpenAI Prompts API with the CORRECTED argument name
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # --- THIS CALL USES 'conversation' INSTEAD OF 'conversation_id' ---
                response = client.responses.create(
                    prompt={
                        "id": "pmpt_690069ca73ac8190a17467e9d9850aec0f5728a89768fdc9", # Use your prompt ID
                        "version": "8",  # Use the latest published version from your prompt
                        "variables": {
                            "user_message": user_input,
                            # conversation_id variable is defined in the prompt, but value comes from the top-level 'conversation' argument below
                        }
                    },
                    # Use the 'conversation' argument for API memory tracking
                    conversation=st.session_state.conversation_id # <-- CORRECTED ARGUMENT NAME
                )
                # --- END OF CORRECTION ---

                # Get the text response
                assistant_response = response.text

                # IMPORTANT: Save the new conversation ID using the correct attribute from the response
                # Based on the error, the response object likely uses 'conversation'
                if hasattr(response, 'conversation'):
                     st.session_state.conversation_id = response.conversation # <-- SAVE CORRECT ATTRIBUTE
                elif hasattr(response, 'conversation_id'): # Check just in case
                     st.session_state.conversation_id = response.conversation_id
                else:
                     # If neither exists, log a warning or handle as needed
                     print("Warning: Response object did not contain 'conversation' or 'conversation_id'")
                     st.session_state.conversation_id = None # Reset if not found? Or keep old one?

                # Display and save the response
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error("Please double-check your prompt ID, version, variable names in the prompt config, ensure the OpenAI library is up-to-date (e.g., openai>=1.0.0 in requirements.txt), and confirm the API key is correctly set in Streamlit secrets.")
