# Data Model: 관리자 질문답변 목록 조회

**Feature**: 001-admin-qa-list  
**Date**: 2026-03-05  
**Phase**: Phase 1 - Data Model Design

## 개요

이 문서는 관리자 질문답변 목록 조회 기능의 데이터 모델을 정의합니다. 모든 모델은 Python 3.11의 dataclass를 사용하며, 타입 힌팅을 통해 명확성을 보장합니다.

## 엔티티 관계도

```text
┌─────────────────────┐
│   QAListItem        │
│                     │
│ - question: str     │
│ - answer: str       │
│ - id: str           │
│ - created_at: str   │
└─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐       ┌──────────────────┐
│  PaginationState    │◄──────│   ListViewState  │
│                     │       │                  │
│ - current_page: int │       │ - items: List    │
│ - total_pages: int  │       │ - is_empty: bool │
│ - items_per_page    │       │ - error: str?    │
│ - total_items: int  │       └──────────────────┘
└─────────────────────┘
```

## 모델 정의

### 1. QAListItem

목록 화면에 표시되는 개별 질문답변 항목을 나타냅니다.

**파일**: `src/models/qa_list_models.py`

```python
"""
QA 목록 조회용 데이터 모델
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


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
```

**필드 설명**:
- `question`: 사용자 질문. ChromaDB의 document 필드에서 가져옴
- `answer`: 관리자가 입력한 답변. ChromaDB metadata["answer"]에서 가져옴
- `id`: ChromaDB 내부 ID (해시 키). 중복 처리 및 업데이트에 사용
- `created_at`: ISO 8601 형식의 생성 시간. 정렬 기준으로 사용
- `metadata`: 추가 메타데이터 (확장성을 위해 보존)

**유효성 규칙**:
- 모든 필수 필드는 비어있지 않아야 함
- `created_at`은 ISO 8601 형식이어야 함 (예: "2026-03-05T10:30:00")

---

### 2. PaginationState

페이징 상태를 관리하는 모델입니다.

**파일**: `src/models/qa_list_models.py`

```python
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
        import math
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
```

**필드 설명**:
- `current_page`: 1부터 시작하는 현재 페이지 번호
- `total_pages`: 전체 페이지 수 (자동 계산됨)
- `items_per_page`: 페이지당 표시할 항목 수 (10, 20, 50만 허용)
- `total_items`: ChromaDB에 저장된 전체 항목 수

**불변성 패턴**:
- 모든 상태 변경 메서드는 새로운 인스턴스를 반환
- Gradio의 State 관리와 호환

---

### 3. ListViewState

전체 목록 뷰의 상태를 나타냅니다.

**파일**: `src/models/qa_list_models.py`

```python
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
```

**필드 설명**:
- `items`: 현재 페이지에 표시할 QAListItem 목록
- `pagination`: 페이징 상태 정보
- `is_empty`: 전체 항목이 없는지 여부 (빈 목록 UI 제어용)
- `error_message`: 오류 발생 시 메시지

**상태 패턴**:
- `empty()`: 항목이 없을 때
- `error()`: 오류 발생 시
- 일반: items가 있고 error_message가 None인 경우

---

## 데이터 흐름

### 1. ChromaDB → QAListItem 변환

```python
# ChromaDBService.get_all_items() 결과:
{
    "ids": ["hash1", "hash2", ...],
    "documents": ["질문1", "질문2", ...],
    "metadatas": [
        {"answer": "답변1", "created_at": "2026-03-05T10:00:00"},
        {"answer": "답변2", "created_at": "2026-03-05T11:00:00"},
        ...
    ]
}

# QAListItem 변환:
items = [
    QAListItem.from_chromadb_result(doc, meta, id)
    for doc, meta, id in zip(documents, metadatas, ids)
]
```

### 2. QAListItem → 정렬 → 페이징

```python
# 1. 정렬 (최신 등록순)
sorted_items = sorted(items, key=lambda x: x.created_at, reverse=True)

# 2. 페이징 상태 생성
pagination = PaginationState(
    current_page=1,
    items_per_page=10,
    total_items=len(sorted_items)
)

# 3. 현재 페이지 항목 추출
offset = pagination.get_offset()
limit = pagination.items_per_page
page_items = sorted_items[offset:offset + limit]

# 4. ListViewState 생성
view_state = ListViewState(
    items=page_items,
    pagination=pagination
)
```

### 3. ListViewState → UI 렌더링

```python
# HTML 카드 렌더링
if view_state.is_empty:
    html = render_empty_message()
elif view_state.has_error():
    html = render_error_message(view_state.error_message)
else:
    html = render_qa_cards(view_state.items)

# 페이징 컨트롤 상태
prev_visible = view_state.pagination.has_prev()
next_visible = view_state.pagination.has_next()
page_info = view_state.pagination.get_page_info_text()
```

---

## 유효성 검증 규칙

### QAListItem
- ✅ `question`: 비어있지 않아야 함, 공백만으로 구성되지 않아야 함
- ✅ `answer`: 비어있지 않아야 함, 공백만으로 구성되지 않아야 함
- ✅ `id`: 비어있지 않아야 함
- ✅ `created_at`: 비어있지 않아야 함, ISO 8601 형식 (YYYY-MM-DDTHH:MM:SS)

### PaginationState
- ✅ `current_page`: 1 이상이어야 함
- ✅ `items_per_page`: 10, 20, 50 중 하나여야 함
- ✅ `total_items`: 0 이상이어야 함
- ✅ `current_page`: `total_pages`를 초과할 수 없음 (자동 조정)

### ListViewState
- ✅ `items`: 리스트여야 함 (빈 리스트 허용)
- ✅ `pagination`: PaginationState 인스턴스여야 함
- ✅ `is_empty`: items와 pagination.total_items가 일관성 있어야 함

---

## 타입 힌팅

모든 모델은 Python의 타입 힌팅을 완전히 활용합니다:

```python
from typing import List, Optional
from dataclasses import dataclass

# mypy로 타입 검사 가능
def process_items(items: List[QAListItem]) -> ListViewState:
    ...
```

**타입 체커 설정** (선택적):
```bash
# mypy 실행
mypy src/models/qa_list_models.py --strict
```

---

## 테스트 전략

### 단위 테스트

**파일**: `tests/unit/test_qa_list_models.py`

```python
def test_qa_list_item_validation():
    """QAListItem 유효성 검증 테스트"""
    # 정상 케이스
    item = QAListItem(
        question="테스트 질문",
        answer="테스트 답변",
        id="test_id",
        created_at="2026-03-05T10:00:00"
    )
    assert item.question == "테스트 질문"
    
    # 빈 질문 - 예외 발생 예상
    with pytest.raises(ValueError):
        QAListItem(question="", answer="답변", id="id", created_at="2026-03-05T10:00:00")

def test_pagination_state_calculations():
    """PaginationState 계산 로직 테스트"""
    state = PaginationState(current_page=2, items_per_page=10, total_items=25)
    
    assert state.total_pages == 3
    assert state.get_offset() == 10
    assert state.has_prev() == True
    assert state.has_next() == True
    assert state.get_page_info_text() == "페이지 2/3"

def test_pagination_state_immutability():
    """PaginationState 불변성 테스트"""
    state1 = PaginationState(current_page=1, items_per_page=10, total_items=50)
    state2 = state1.next_page()
    
    assert state1.current_page == 1  # 원본 불변
    assert state2.current_page == 2  # 새 인스턴스

def test_list_view_state_empty():
    """빈 목록 상태 테스트"""
    state = ListViewState.empty()
    
    assert state.is_empty == True
    assert len(state.items) == 0
    assert state.get_display_message() == "등록된 질문답변이 없습니다"
```

---

## 마이그레이션 가이드

### 기존 ChromaDB 데이터에 created_at 추가

```python
def migrate_add_created_at():
    """기존 QA 항목에 created_at 추가
    
    한 번만 실행되어야 함. 이미 created_at이 있는 항목은 건너뜀.
    """
    from datetime import datetime, timedelta
    from src.services.chromadb_service import ChromaDBService
    
    service = ChromaDBService()
    results = service.collection.get(include=["documents", "metadatas"])
    
    ids_to_update = []
    metadatas_to_update = []
    
    base_time = datetime(2026, 1, 1)  # 기준 시간
    
    for i, (id, metadata) in enumerate(zip(results["ids"], results["metadatas"])):
        if "created_at" not in metadata:
            # 인덱스 기반으로 시간 할당 (역순)
            timestamp = base_time + timedelta(minutes=i)
            metadata["created_at"] = timestamp.isoformat()
            
            ids_to_update.append(id)
            metadatas_to_update.append(metadata)
    
    if ids_to_update:
        service.collection.update(
            ids=ids_to_update,
            metadatas=metadatas_to_update
        )
        print(f"✅ {len(ids_to_update)}개 항목에 created_at 추가 완료")
    else:
        print("✅ 모든 항목에 이미 created_at이 존재함")
```

**실행 방법**:
```bash
# 마이그레이션 스크립트 실행
python -m scripts.migrate_add_created_at
```

---

## 다음 단계

- ✅ `research.md`: 완료
- ✅ `data-model.md`: 완료 (이 파일)
- ⏭️ `contracts/`: (해당 없음 - 읽기 전용 기능)
- ⏭️ `quickstart.md`: 개발자 가이드 생성
- ⏭️ Agent context 업데이트
