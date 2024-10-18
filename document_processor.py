import os
import tempfile
import uuid
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from streamlit.runtime.uploaded_file_manager import UploadedFile

from constants import CHUNK_SIZE, CHUNK_OVERLAP
from utils import count_tokens


def load_document(file: UploadedFile) -> List[Document]:
    """Load document from file."""
    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        # 안전한 파일 이름 생성
        safe_filename = str(uuid.uuid4()) + os.path.splitext(file.name)[1]
        temp_file_path = os.path.join(temp_dir, safe_filename)

        # 업로드된 파일을 임시 위치에 저장
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file.getvalue())

        # 파일 확장자에 따라 적절한 문서 로더 선택
        if file.name.endswith('.pdf'):
            loader = PyPDFLoader(temp_file_path)
        elif file.name.endswith('.docx'):
            loader = Docx2txtLoader(temp_file_path)
        elif file.name.endswith('.pptx'):
            loader = UnstructuredPowerPointLoader(temp_file_path)
        else:
            raise ValueError(f"Unsupported file type: {file.name}")

        # 문서 로드 및 분할
        documents = loader.load_and_split()

    # 임시 디렉토리 및 파일은 이 지점에서 자동으로 삭제됨
    return documents


def process_documents(files: List[UploadedFile]) -> List[Document]:
    """Process uploaded documents."""
    documents = []
    for file in files:
        documents.extend(load_document(file))
    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=count_tokens
    )
    return text_splitter.split_documents(documents)
