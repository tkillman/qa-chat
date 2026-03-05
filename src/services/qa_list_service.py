"""QA 목록 조회 서비스

관리자가 등록된 Q&A 항목을 페이징하여 조회하는 기능을 제공합니다.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.qa_list_models import QAListItem, PaginationState, ListViewState
from services.chromadb_service import get_chromadb_service
from services.langfuse_service import get_langfuse_service

logger = logging.getLogger(__name__)


class QAListService:
    """Q&A 목록 조회 서비스
    
    ChromaDB에서 Q&A 항목을 조회하고, 정렬하고, 페이징하여 반환합니다.
    Langfuse를 통해 모든 작업을 추적합니다.
    """
    
    def __init__(self):
        """서비스 초기화"""
        self.chromadb_service = get_chromadb_service()
        self.langfuse = get_langfuse_service()
    
    def list_items(
        self,
        page: int = 1,
        items_per_page: int = 10
    ) -> ListViewState:
        """Q&A 항목 목록 조회
        
        Args:
            page: 페이지 번호 (1부터 시작)
            items_per_page: 페이지당 항목 수 (10, 20, 50)
            
        Returns:
            ListViewState: 목록 뷰 상태 (항목, 페이징 정보, 오류 메시지)
        """
        try:
            # Step 0: 컬렉션 상태 확인
            try:
                self.chromadb_service._ensure_collection_healthy()
            except Exception as e:
                logger.error(f"컬렉션 재생성 실패: {e}")
                raise
            
            # Step 1: ChromaDB에서 모든 항목 조회
            all_items = []
            try:
                results = self.chromadb_service.collection.get(
                    include=["documents", "metadatas"]
                )
                
                # docs, metas, ids의 개수가 일치하는지 확인
                docs = results.get("documents", [])
                metas = results.get("metadatas", [])
                ids = results.get("ids", [])
                
                logger.debug(f"ChromaDB results - docs: {len(docs)}, metas: {len(metas)}, ids: {len(ids)}")
                
                # ChromaDB 결과를 QAListItem으로 변환
                for doc, metadata, id in zip(docs, metas, ids):
                    try:
                        item = QAListItem.from_chromadb_result(doc, metadata, id)
                        all_items.append(item)
                    except ValueError as e:
                        logger.warning(f"유효하지 않은 항목 건너뜀: {id}, 오류: {e}")
                        continue
            except Exception as e:
                logger.error(f"ChromaDB 조회 실패: {e}")
                raise
            
            # 항목이 없으면 빈 상태 반환
            if not all_items:
                self.langfuse.log_event(
                    "admin_list_qa_items",
                    {
                        "page": page,
                        "items_per_page": items_per_page,
                        "total_items": 0,
                        "result": "empty",
                        "success": True
                    }
                )
                return ListViewState.empty()
            
            # Step 2: 최신 등록순(내림차순)으로 정렬
            sorted_items = sorted(
                all_items,
                key=lambda x: x.created_at,
                reverse=True  # 내림차순 (최신이 먼저)
            )
            
            # Step 3: 페이징 상태 생성
            pagination = PaginationState(
                current_page=page,
                items_per_page=items_per_page,
                total_items=len(sorted_items)
            )
            
            # Step 4: 현재 페이지 항목 추출
            offset = pagination.get_offset()
            end_index = offset + items_per_page
            
            paginated_items = sorted_items[offset:end_index]
            
            # ListViewState 생성
            view_state = ListViewState(
                items=paginated_items,
                pagination=pagination,
                is_empty=False
            )
            
            # Langfuse 로깅
            self.langfuse.log_event(
                "admin_list_qa_items",
                {
                    "page": page,
                    "items_per_page": items_per_page,
                    "total_items": len(sorted_items),
                    "returned_count": len(paginated_items),
                    "total_pages": pagination.total_pages,
                    "success": True
                }
            )
            
            return view_state
            
        except Exception as e:
            logger.error(f"목록 조회 실패: {e}", exc_info=True)
            
            # 오류 상태 반환
            error_message = f"목록 조회 중 오류 발생: {str(e)}"
            
            self.langfuse.log_error(
                "admin_list_qa_items",
                error_message,
                {
                    "page": page,
                    "items_per_page": items_per_page,
                    "error": str(e)
                }
            )
            
            return ListViewState.error(error_message)
    
    def search_items(
        self,
        query: str,
        page: int = 1,
        items_per_page: int = 10
    ) -> ListViewState:
        """Q&A 항목 검색 (선택적)
        
        Args:
            query: 검색 쿼리
            page: 페이지 번호
            items_per_page: 페이지당 항목 수
            
        Returns:
            ListViewState: 검색 결과
            
        Note:
            이 메서드는 향후 구현 예정입니다.
        """
        raise NotImplementedError("검색 기능은 향후 구현 예정입니다")


# 싱글톤 인스턴스
_qa_list_service_instance: Optional[QAListService] = None


def get_qa_list_service() -> QAListService:
    """QAListService 싱글톤 팩토리
    
    Returns:
        QAListService: 싱글톤 인스턴스
    """
    global _qa_list_service_instance
    
    if _qa_list_service_instance is None:
        _qa_list_service_instance = QAListService()
    
    return _qa_list_service_instance
