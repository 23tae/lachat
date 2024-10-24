import os
import streamlit as st
from loguru import logger
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback

from utils import validate_api_key, init_session_state, on_click_copy
from document_processor import process_documents, split_documents
from vector_store import create_vector_store
from conversation_chain import create_conversation_chain


def main():
    # 환경 변수 로드 및 기본 API 키 설정
    load_dotenv()
    default_api_key = os.getenv("OPENAI_API_KEY", "")

    # Streamlit 페이지 설정
    st.set_page_config(page_title="LaChat", page_icon=":seedling:")
    st.title("_Ask Me Anything_ :palm_tree:")

    # 세션 상태 초기화
    init_session_state()
    count = 0

    # 사이드바 UI 구성
    with st.sidebar:
        uploaded_files = st.file_uploader(
            "Upload files", type=['pdf', 'docx', 'pptx'], accept_multiple_files=True)
        openai_api_key = st.text_input(
            "OpenAI API Key", key="chatbot_api_key", type="password", value=default_api_key)
        process = st.button("Start Processing")

    # 문서 처리 로직
    if process:
        if not openai_api_key:
            st.error("Please enter your OpenAI API key.")
            st.stop()

        if not validate_api_key(openai_api_key):
            st.error("Invalid OpenAI API key.")
            st.stop()

        # 문서 처리 및 벡터 저장소 생성
        with st.spinner("Processing documents..."):
            documents = process_documents(uploaded_files)
            text_chunks = split_documents(documents)
            vector_store = create_vector_store(text_chunks)
            st.session_state.conversation = create_conversation_chain(
                vector_store, openai_api_key)
            st.session_state.process_complete = True

        st.success("Documents processed successfully!")

    # 채팅 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if query := st.chat_input("Enter your question."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            if not st.session_state.process_complete:
                st.error(
                    "Please upload and process documents before asking questions.")
                st.stop()

            # 대화 체인을 통한 응답 생성
            chain = st.session_state.conversation
            with st.spinner("Thinking..."):
                with get_openai_callback() as cb:
                    result = chain({"question": query})
                    st.session_state.chat_history = result['chat_history']
                response = result['answer']
                source_documents = result['source_documents']

                st.markdown(response)
                st.button("📋", on_click=on_click_copy,
                          args=(response, ), key=count)
                logger.info(f"Current Count: {count}")
                count += 1
                with st.expander("View Source Documents"):
                    for doc in source_documents:
                        st.markdown(
                            doc.metadata['source'], help=doc.page_content)

                # 토큰 사용량 및 비용 로깅
                logger.info(f"Total Tokens: {cb.total_tokens}")
                logger.info(f"Prompt Tokens: {cb.prompt_tokens}")
                logger.info(f"Completion Tokens: {cb.completion_tokens}")
                logger.info(f"Total Cost (USD): ${cb.total_cost}")

        st.session_state.messages.append(
            {"role": "assistant", "content": response})


if __name__ == '__main__':
    main()
