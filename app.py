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
st.write("Using prompt: pmpt_690069ca73ac8190a17467e9d9850aec0f5728a89768fdc9")

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
if prompt := st.chat_input("What is up?"):
    
    # 1. Add user's message to UI and history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call the OpenAI Prompts API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.responses.create(
                    prompt={
                        "id": "pmpt_690069ca73ac8190a17467e9d9850aec0f5728a89768fdc9",
                        "version": "1"  # Or your specific version
                    },
                    # This is the "chat" part. We pass the user's message
                    # and the conversation ID to maintain memory.
                    variables={
                        "user_message": prompt 
                    },
                    conversation_id=st.session_state.conversation_id
                )
                
                # Get the text response
                assistant_response = response.text
                
                # IMPORTANT: Save the new conversation_id for the next turn
                st.session_state.conversation_id = response.conversation_id
                
                # Display and save the response
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error("Please check that your prompt is configured with a 'user_message' variable and the 'conversation_id' parameter.")
