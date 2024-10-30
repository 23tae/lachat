import os
import streamlit as st
from loguru import logger
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback

from utils import validate_api_key, init_session_state, copy_to_clipboard
from document_processor import split_documents, DocumentProcessor
from vector_store import VectorStoreManager
from conversation_chain import create_conversation_chain


os.environ["TOKENIZERS_PARALLELISM"] = "false"


def main():
    # 환경 변수 로드 및 기본 API 키 설정
    load_dotenv()
    default_api_key = os.getenv("OPENAI_API_KEY", "")

    # Streamlit 페이지 설정
    st.set_page_config(page_title="LaChat", page_icon=":seedling:")
    st.title("무엇을 도와드릴까요? :palm_tree:")

    # 세션 상태 초기화
    init_session_state()

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
            doc_processor = DocumentProcessor()
            vector_store_manager = VectorStoreManager()

            documents, cached_docs_count = doc_processor.process_documents(
                uploaded_files)
            text_chunks = split_documents(documents)
            vector_store, from_cache = vector_store_manager.create_vector_store(
                text_chunks)

            st.session_state.conversation = create_conversation_chain(
                vector_store, openai_api_key)
            st.session_state.process_complete = True

            if cached_docs_count > 0:
                cached_status = "재사용된 문서" if cached_docs_count == len(
                    uploaded_files) else "일부 재사용된 문서"
                vs_status = "재사용된" if from_cache else "새로 생성된"
                st.info(f"{cached_status}와 {vs_status} 벡터 스토어를 사용하여 처리되었습니다.")
            else:
                st.info("모든 문서가 새로 처리되었습니다.")

        st.success("Documents processed successfully!")

    # 채팅 메시지 표시
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                button_key = f"copy_button_{i}"
                if st.button("📋", key=button_key, help="Copy"):
                    if copy_to_clipboard(message["content"]):
                        st.toast("클립보드에 복사되었습니다!", icon="✅")
                    else:
                        st.toast("복사에 실패했습니다. 다시 시도해주세요.", icon="❌")
                    st.session_state.copy_buttons[button_key] = True

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
                button_key = f"copy_button_{len(st.session_state.messages)}"
                if st.button("📋", key=button_key, help="Copy"):
                    if copy_to_clipboard(response):
                        st.toast("클립보드에 복사되었습니다!", icon="✅")
                    else:
                        st.toast("복사에 실패했습니다. 다시 시도해주세요.", icon="❌")
                    st.session_state.copy_buttons[button_key] = True

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
