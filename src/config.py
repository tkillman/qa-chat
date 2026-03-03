"""
QA Chat 설정
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 관리자 설정
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")

# ChromaDB 설정
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
SEARCH_TOP_K_USER = int(os.getenv("SEARCH_TOP_K_USER", "1"))
SEARCH_TOP_K_ADMIN = int(os.getenv("SEARCH_TOP_K_ADMIN", "5"))

# Langfuse 설정
LANGFUSE_API_KEY = os.getenv("LANGFUSE_API_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# 입력 길이 제한
MAX_USER_QUESTION_LENGTH = int(os.getenv("MAX_USER_QUESTION_LENGTH", "500"))
MAX_ADMIN_QUESTION_LENGTH = int(os.getenv("MAX_ADMIN_QUESTION_LENGTH", "500"))
MAX_ADMIN_ANSWER_LENGTH = int(os.getenv("MAX_ADMIN_ANSWER_LENGTH", "2000"))

# init.txt 경로
INIT_FILE_PATH = os.getenv("INIT_FILE_PATH", "data/init.txt")

# Embedding 모델 (기본값: OpenAI, 추후 research.md에서 결정)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# 로깅
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/qa_chat.log")
