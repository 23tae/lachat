from typing import List, Optional, Tuple
import os
import hashlib
import shutil
from loguru import logger
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from constants import EMBEDDING_MODEL_NAME, CACHE_DIR


class VectorStoreManager:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = os.path.join(cache_dir, "vector_stores")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def _get_documents_hash(self, documents: List[Document]) -> str:
        """문서 내용과 메타데이터를 기반으로 일관된 해시 생성."""
        # 문서 정보를 정렬된 형태로 처리하여 일관성 보장
        doc_infos = []
        for doc in documents:
            doc_info = {
                'content': doc.page_content,
                'metadata': sorted(doc.metadata.items())  # 메타데이터 키 정렬
            }
            doc_infos.append(doc_info)

        # 정렬된 문서 정보를 기반으로 해시 생성
        doc_infos.sort(key=lambda x: x['content'])  # 문서 내용으로 정렬
        content_str = str(doc_infos)  # 전체 정보를 문자열로 변환
        return hashlib.md5(content_str.encode()).hexdigest()

    def _get_cache_path(self, docs_hash: str) -> str:
        """벡터 스토어 캐시 경로 생성."""
        return os.path.join(self.cache_dir, f"vs_{docs_hash}")

    def _load_from_cache(self, docs_hash: str) -> Optional[FAISS]:
        """캐시된 벡터 스토어 로드."""
        cache_path = self._get_cache_path(docs_hash)
        try:
            if os.path.exists(cache_path):
                return FAISS.load_local(
                    cache_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
        except Exception as e:
            logger.warning(f"Failed to load vector store from cache: {e}")
            if os.path.exists(cache_path):
                shutil.rmtree(cache_path)  # 손상된 캐시 제거
            return None
        return None

    def _save_to_cache(self, vector_store: FAISS, docs_hash: str):
        """벡터 스토어를 캐시에 저장."""
        cache_path = self._get_cache_path(docs_hash)
        try:
            if os.path.exists(cache_path):
                shutil.rmtree(cache_path)  # 기존 캐시 제거
            vector_store.save_local(cache_path)
        except Exception as e:
            logger.error(f"Failed to save vector store to cache: {e}")

    def create_vector_store(self, documents: List[Document]) -> Tuple[FAISS, bool]:
        """문서로부터 벡터 스토어 생성 또는 로드."""
        docs_hash = self._get_documents_hash(documents)

        # 캐시된 벡터 스토어 확인
        cached_store = self._load_from_cache(docs_hash)
        if cached_store is not None:
            logger.info("Using cached vector store")
            return cached_store, True

        # 새로운 벡터 스토어 생성
        logger.info("Creating new vector store")
        vector_store = FAISS.from_documents(documents, self.embeddings)
        self._save_to_cache(vector_store, docs_hash)
        return vector_store, False
