import os
import tempfile
import uuid
import hashlib
import pickle
from typing import List, Tuple, Optional
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from streamlit.runtime.uploaded_file_manager import UploadedFile

from constants import CHUNK_SIZE, CHUNK_OVERLAP, CACHE_DIR
from utils import count_tokens


class DocumentProcessor:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_file_hash(self, file: UploadedFile) -> str:
        """Generate hash from file content and metadata."""
        content = file.getvalue()
        metadata = f"{file.name}{file.size}{file.type}"
        return hashlib.md5(content + metadata.encode()).hexdigest()

    def _get_cache_path(self, file_hash: str) -> str:
        """Get cache file path."""
        return os.path.join(self.cache_dir, f"{file_hash}.pkl")

    def _save_to_cache(self, documents: List[Document], file_hash: str):
        """Save processed documents to cache."""
        cache_path = self._get_cache_path(file_hash)
        with open(cache_path, 'wb') as f:
            pickle.dump(documents, f)

    def _load_from_cache(self, file_hash: str) -> Optional[List[Document]]:
        """Load processed documents from cache."""
        cache_path = self._get_cache_path(file_hash)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except:
                return None
        return None

    def load_document(self, file: UploadedFile) -> Tuple[List[Document], bool]:
        """Load document from file or cache."""
        file_hash = self._get_file_hash(file)

        # Try to load from cache first
        cached_docs = self._load_from_cache(file_hash)
        if cached_docs is not None:
            return cached_docs, True

        # Process the file if not in cache
        with tempfile.TemporaryDirectory() as temp_dir:
            safe_filename = str(uuid.uuid4()) + os.path.splitext(file.name)[1]
            temp_file_path = os.path.join(temp_dir, safe_filename)

            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file.getvalue())

            if file.name.endswith('.pdf'):
                loader = PyPDFLoader(temp_file_path)
            elif file.name.endswith('.docx'):
                loader = Docx2txtLoader(temp_file_path)
            elif file.name.endswith('.pptx'):
                loader = UnstructuredPowerPointLoader(temp_file_path)
            else:
                raise ValueError(f"Unsupported file type: {file.name}")

            documents = loader.load_and_split()

        # Save to cache
        self._save_to_cache(documents, file_hash)
        return documents, False

    def process_documents(self, files: List[UploadedFile]) -> Tuple[List[Document], int]:
        """Process uploaded documents and return number of cached files used."""
        documents = []
        cached_count = 0

        for file in files:
            docs, from_cache = self.load_document(file)
            documents.extend(docs)
            if from_cache:
                cached_count += 1

        return documents, cached_count


def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=count_tokens
    )
    return text_splitter.split_documents(documents)
