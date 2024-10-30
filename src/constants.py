import os


DEFAULT_MODEL_NAME = "gpt-4o-mini"
EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 100
MAX_MEMORY_LENGTH = 50
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CACHE_DIR = os.path.join(PROJECT_ROOT, ".cache")
