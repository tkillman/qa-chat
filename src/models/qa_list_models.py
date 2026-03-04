"""QA 목록 조회용 데이터 모델

이 모듈은 관리자 Q&A 목록 조회 기능에서 사용되는 데이터 모델을 정의합니다.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import math


@dataclass
class QAListItem:
    """목록에 표시되는 QA 항목
    
    Attributes:
        question (str): 질문 텍스트
        answer (str): 답변 텍스트
        id (str): ChromaDB 내부 ID (해시 키)
        created_at (str): 생성 시간 (ISO 8601 형식)
        metadata (dict): 추가 메타데이터 (선택적)
    """
    question: str
    answer: str
    id: str
    created_at: str
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        """초기화 후 유효성 검증"""
        if not self.question or not self.question.strip():
            raise ValueError("Question cannot be empty")
        if not self.answer or not self.answer.strip():
            raise ValueError("Answer cannot be empty")
        if not self.id:
            raise ValueError("ID cannot be empty")
        if not self.created_at:
            raise ValueError("created_at cannot be empty")
    
    @classmethod
    def from_chromadb_result(cls, doc: str, metadata: dict, id: str) -> "QAListItem":
        """ChromaDB 결과에서 QAListItem 생성
        
        Args:
            doc: ChromaDB document (질문 텍스트)
            metadata: ChromaDB metadata (답변 + created_at 포함)
            id: ChromaDB ID
            
        Returns:
            QAListItem 인스턴스
            
        Raises:
            ValueError: 필수 필드 누락 시
        """
        answer = metadata.get("answer", "")
        created_at = metadata.get("created_at", "")
        
        # created_at이 없는 경우 (마이그레이션 전 데이터)
        if not created_at:
            created_at = datetime(2000, 1, 1).isoformat()  # 기본값
        
        return cls(
            question=doc,
            answer=answer,
            id=id,
            created_at=created_at,
            metadata=metadata
        )
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환 (직렬화용)"""
        return {
            "question": self.question,
            "answer": self.answer,
            "id": self.id,
            "created_at": self.created_at,
            "metadata": self.metadata
        }


@dataclass
class PaginationState:
    """페이징 상태 정보
    
    Attributes:
        current_page (int): 현재 페이지 번호 (1부터 시작)
        total_pages (int): 전체 페이지 수
        items_per_page (int): 페이지당 항목 수 (10, 20, 50 중 하나)
        total_items (int): 전체 항목 수
    """
    current_page: int = 1
    total_pages: int = 1
    items_per_page: int = 10
    total_items: int = 0
    
    def __post_init__(self):
        """초기화 후 유효성 검증 및 계산"""
        # 음수 방지
        if self.current_page < 1:
            self.current_page = 1
        if self.total_items < 0:
            self.total_items = 0
        if self.items_per_page not in [10, 20, 50]:
            raise ValueError(f"items_per_page must be 10, 20, or 50, got {self.items_per_page}")
        
        # 전체 페이지 수 계산
        if self.total_items > 0:
            self.total_pages = math.ceil(self.total_items / self.items_per_page)
        else:
            self.total_pages = 1
        
        # 현재 페이지가 범위를 벗어나면 조정
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
    
    def has_prev(self) -> bool:
        """이전 페이지 존재 여부"""
        return self.current_page > 1
    
    def has_next(self) -> bool:
        """다음 페이지 존재 여부"""
        return self.current_page < self.total_pages
    
    def get_offset(self) -> int:
        """현재 페이지의 시작 인덱스(offset) 계산"""
        return (self.current_page - 1) * self.items_per_page
    
    def get_page_info_text(self) -> str:
        """페이지 정보 텍스트 생성 (UI용)"""
        return f"페이지 {self.current_page}/{self.total_pages}"
    
    def get_total_items_text(self) -> str:
        """총 항목 수 텍스트 생성 (UI용)"""
        return f"총 {self.total_items}개의 항목"
    
    def next_page(self) -> "PaginationState":
        """다음 페이지로 이동한 새 상태 반환 (불변)"""
        if not self.has_next():
            return self
        
        return PaginationState(
            current_page=self.current_page + 1,
            total_pages=self.total_pages,
            items_per_page=self.items_per_page,
            total_items=self.total_items
        )
    
    def prev_page(self) -> "PaginationState":
        """이전 페이지로 이동한 새 상태 반환 (불변)"""
        if not self.has_prev():
            return self
        
        return PaginationState(
            current_page=self.current_page - 1,
            total_pages=self.total_pages,
            items_per_page=self.items_per_page,
            total_items=self.total_items
        )
    
    def change_items_per_page(self, new_items_per_page: int) -> "PaginationState":
        """페이지당 항목 수 변경 (첫 페이지로 이동)"""
        return PaginationState(
            current_page=1,  # 첫 페이지로 리셋
            total_pages=0,   # 재계산됨
            items_per_page=new_items_per_page,
            total_items=self.total_items
        )


@dataclass
class ListViewState:
    """목록 뷰의 전체 상태
    
    Attributes:
        items (List[QAListItem]): 현재 페이지에 표시할 항목들
        pagination (PaginationState): 페이징 상태
        is_empty (bool): 항목이 없는지 여부
        error_message (Optional[str]): 오류 메시지 (있을 경우)
    """
    items: list[QAListItem]
    pagination: PaginationState
    is_empty: bool = False
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """초기화 후 상태 계산"""
        self.is_empty = len(self.items) == 0 and self.pagination.total_items == 0
    
    @classmethod
    def empty(cls) -> "ListViewState":
        """빈 목록 상태 생성"""
        return cls(
            items=[],
            pagination=PaginationState(total_items=0),
            is_empty=True
        )
    
    @classmethod
    def error(cls, message: str) -> "ListViewState":
        """오류 상태 생성"""
        return cls(
            items=[],
            pagination=PaginationState(total_items=0),
            is_empty=True,
            error_message=message
        )
    
    def has_error(self) -> bool:
        """오류가 있는지 확인"""
        return self.error_message is not None
    
    def get_display_message(self) -> str:
        """표시할 메시지 반환 (빈 목록 또는 오류)"""
        if self.has_error():
            return self.error_message
        if self.is_empty:
            return "등록된 질문답변이 없습니다"
        return ""
