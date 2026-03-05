from pathlib import Path

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"

INFERENCE_MODEL = "qwen/qwen3.5-9b"
EMBEDDING_MODEL = "text-embedding-mxbai-embed-large-v1"

DOCS_DIR = Path(__file__).resolve().parent.parent / "GraphXR-WEB" / "asciidoc" / "3-x"
CHROMA_DIR = Path(__file__).resolve().parent / "chroma_db"
COLLECTION_NAME = "graphxr_docs"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5
