import streamlit as st
import tiktoken
import openai
from loguru import logger
import pyperclip


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key."""
    try:
        openai.api_key = api_key
        openai.models.list()
        return True
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return False


def init_session_state():
    """Initialize session state if not exists."""
    state_keys = {
        "conversation": None,
        "chat_history": None,
        "process_complete": False,
        "copy_buttons": {},
        "messages": [{"role": "assistant", "content": "업로드한 문서에 대해 질문해주세요."}]
    }

    for key, value in state_keys.items():
        if key not in st.session_state:
            st.session_state[key] = value


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text."""
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)


def copy_to_clipboard(text):
    """
    클립보드에 텍스트를 복사
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        logger.error(f"Failed to copy text: {e}")
        return False
