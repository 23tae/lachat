import streamlit as st
import tiktoken
import openai
from loguru import logger

def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key."""
    try:
        openai.api_key = api_key
        openai.models.list()
        return True
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return False

def init_session_state(key: str, default_value=None):
    """Initialize session state if not exists."""
    if key not in st.session_state:
        st.session_state[key] = default_value

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text."""
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)