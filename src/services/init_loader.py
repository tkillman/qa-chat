"""
초기 로드 서비스 - init.txt에서 ChromaDB로 로드
"""
import logging
import time
from typing import Tuple
from src.services.file_service import FileService
from src.services.chromadb_service import ChromaDBService
from src.services.langfuse_service import get_langfuse_service
from src.config import INIT_FILE_PATH

logger = logging.getLogger(__name__)


class InitLoader:
    """초기 데이터 로드 관리자 (US1)"""
    
    def __init__(self):
        """InitLoader 초기화"""
        self.file_service = FileService()
        self.langfuse = get_langfuse_service()
    
    def load_initial_data(self) -> Tuple[int, float, bool]:
        """init.txt에서 ChromaDB로 초기 데이터 로드 (US1)
        
        Spec FR-001, FR-003, FR-005 참고:
        - init.txt를 줄 단위 JSON으로 읽기
        - ChromaDB에 임베딩과 함께 저장
        - Langfuse로 추적
        
        Returns:
            (로드된 항목 수, 소요 시간(ms), 성공 여부)
            
        Raises:
            RuntimeError: 로드 실패 시
        """
        start_time = time.time()
        
        try:
            logger.info("Starting initial data load from init.txt")
            
            # 1. init.txt 읽기
            items = FileService.read_qa_items(INIT_FILE_PATH)
            logger.info(f"Read {len(items)} items from init.txt")
            
            # 2. ChromaDB 초기화 및 데이터 추가
            chroma = ChromaDBService()
            
            if items:
                # 기존 데이터 제거 (새로 시작)
                chroma.clear_collection()
                
                # 새 데이터 추가
                chroma.add_qa_items(items)
                logger.info(f"Added {len(items)} items to ChromaDB")
            else:
                # init.txt가 비어있거나 없으면 빈 상태로 시작
                chroma.clear_collection()
                logger.info("Starting with empty ChromaDB (no items in init.txt)")
            
            # 3. 성공 시간 기록
            duration_ms = (time.time() - start_time) * 1000
            
            # 4. Langfuse 추적 (US1에 대한 관찰성)
            self.langfuse.log_initial_load(
                num_items=len(items),
                duration_ms=duration_ms,
                success=True
            )
            
            logger.info(f"Initial load completed: {len(items)} items in {duration_ms:.2f}ms")
            return len(items), duration_ms, True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"Error during initial load: {e}")
            
            # 에러 추적
            self.langfuse.log_error(
                error_type="initial_load_failed",
                error_message=str(e),
                context={"duration_ms": duration_ms}
            )
            
            # 빈 상태로 계속 진행 (Spec EC2: 형식 오류 시 기본값 처리)
            try:
                chroma = ChromaDBService()
                chroma.clear_collection()
                logger.info("Initialized empty ChromaDB after error")
            except Exception as cleanup_error:
                logger.warning(f"Failed to initialize empty ChromaDB: {cleanup_error}")
            
            return 0, duration_ms, False


# 글로벌 인스턴스
_init_loader: InitLoader | None = None


def get_init_loader() -> InitLoader:
    """InitLoader 인스턴스 반환 (싱글톤)
    
    Returns:
        InitLoader 인스턴스
    """
    global _init_loader
    if _init_loader is None:
        _init_loader = InitLoader()
    return _init_loader
