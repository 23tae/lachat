from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS

from constants import DEFAULT_MODEL_NAME, MAX_MEMORY_LENGTH


def create_conversation_chain(vector_store: FAISS, openai_api_key: str) -> ConversationalRetrievalChain:
    """Create conversation chain."""
    # OpenAI 챗봇 모델 초기화
    llm = ChatOpenAI(openai_api_key=openai_api_key,
                     model_name=DEFAULT_MODEL_NAME, temperature=0)

    # 대화 기록을 저장할 메모리 초기화
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer',
        max_memory_length=MAX_MEMORY_LENGTH
    )

    # ConversationalRetrievalChain 생성
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_type='mmr', verbose=True),
        memory=memory,
        get_chat_history=lambda h: h,
        return_source_documents=True,
        verbose=True
    )
