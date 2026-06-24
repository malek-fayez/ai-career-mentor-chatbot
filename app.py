import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from prompts import SYSTEM_PROMPT
from utils.memory import (
    init_memory,
    add_message,
    get_messages,
    clear_memory,
    memory_size,
)
from utils.retriever import retrieve_context


load_dotenv(dotenv_path=Path(__file__).parent / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

st.set_page_config(
    page_title="AI Career Mentor Chatbot",
    page_icon="🤖",
    layout="centered"
)

init_memory()

st.title("AI Career Mentor Chatbot with Memory")
st.caption(
    "A Streamlit GenAI chatbot that remembers the current session "
    "and helps with AI career guidance."
)


if not GROQ_API_KEY:
    st.error("Groq API key not found. Please check your .env file.")
    st.info("Your .env file should contain: GROQ_API_KEY=your_real_key_here")
    st.stop()


client = Groq(api_key=GROQ_API_KEY)


def build_messages(retrieved_context=""):
    """
    Builds the message list sent to the Groq LLM.
    This is the memory mechanism:
    the previous user and assistant messages are sent again with each new request.
    """

    system_content = SYSTEM_PROMPT

    if retrieved_context:
        system_content += f"""

Use this local knowledge base context when relevant:

{retrieved_context}
"""

    messages = [
        {
            "role": "system",
            "content": system_content
        }
    ]

    messages.extend(get_messages())

    return messages


with st.sidebar:
    st.header("Chatbot Controls")

    st.write(f"Messages in memory: **{memory_size()}**")
    st.write(f"Model: `{MODEL_NAME}`")

    use_knowledge_base = st.toggle(
        "Use local AI knowledge base",
        value=True
    )

    if st.button("Clear chat"):
        clear_memory()
        st.rerun()

    conversation_text = ""
    for message in get_messages():
        role = message["role"].upper()
        content = message["content"]
        conversation_text += f"{role}: {content}\n\n"

    st.download_button(
        label="Download conversation",
        data=conversation_text,
        file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )


for message in get_messages():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_input = st.chat_input(
    "Ask about AI, internships, CVs, GitHub projects, or learning roadmaps..."
)


if user_input:
    user_input = user_input.strip()

    if not user_input:
        st.warning("Please enter a valid message.")
        st.stop()

    add_message("user", user_input)

    with st.chat_message("user"):
        st.markdown(user_input)

    retrieved_context = ""
    if use_knowledge_base:
        retrieved_context = retrieve_context(user_input)

    api_messages = build_messages(retrieved_context=retrieved_context)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=api_messages,
                    temperature=0.7,
                    max_tokens=700
                )

                assistant_reply = response.choices[0].message.content

            except Exception as error:
                assistant_reply = (
                    "An error occurred while contacting the Groq model.\n\n"
                    f"Error details: `{error}`"
                )

        st.markdown(assistant_reply)

    add_message("assistant", assistant_reply)