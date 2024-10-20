from typing import List
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from constants import EMBEDDING_MODEL_NAME


def create_vector_store(documents: List[Document]) -> FAISS:
    """Create vector store from documents."""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    return FAISS.from_documents(documents, embeddings)
