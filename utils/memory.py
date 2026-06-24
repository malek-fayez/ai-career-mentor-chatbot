import streamlit as st

MAX_MESSAGES = 12


def init_memory():
    """
    Initializes chat memory inside Streamlit session state.
    This keeps messages alive during the active browser session.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []


def add_message(role, content):
    """
    Adds a user or assistant message to memory.
    """
    st.session_state.messages.append({
        "role": role,
        "content": content
    })
    prune_memory()


def get_messages():
    """
    Returns the current chat history.
    """
    return st.session_state.messages


def clear_memory():
    """
    Clears the current chat history.
    """
    st.session_state.messages = []


def memory_size():
    """
    Returns the number of stored messages.
    """
    return len(st.session_state.messages)


def prune_memory(max_messages=MAX_MESSAGES):
    """
    Sliding-window memory:
    keeps only the latest messages to avoid sending very long conversations.
    """
    if len(st.session_state.messages) > max_messages:
        st.session_state.messages = st.session_state.messages[-max_messages:]


def format_messages_for_api(system_prompt, retrieved_context=None):
    """
    Converts Streamlit memory into the format expected by the OpenAI Responses API.
    """
    api_messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    if retrieved_context:
        api_messages.append({
            "role": "system",
            "content": f"Use this local knowledge base context when relevant:\n\n{retrieved_context}"
        })

    api_messages.extend(st.session_state.messages)

    return api_messages