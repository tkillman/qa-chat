# Quickstart: 관리자 질문답변 목록 조회

**Feature**: 001-admin-qa-list  
**Date**: 2026-03-05  
**Target Audience**: 개발자

## 🎯 목표

이 가이드를 통해 5분 안에:
1. 기능의 전체 구조 이해
2. 로컬 개발 환경 설정
3. 첫 번째 테스트 실행
4. UI 컴포넌트 확인

## 📋 전제 조건

```bash
# Python 3.11+
python --version

# 가상 환경 활성화
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

## 🏗️ 아키텍처 개요

```text
┌─────────────────────────────────────────────────┐
│              Gradio UI Layer                    │
│  (src/ui/admin_list_tab.py)                     │
│  - 카드 렌더링                                    │
│  - 페이징 컨트롤                                  │
│  - 이벤트 핸들러                                  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│          Service Layer                          │
│  (src/services/qa_list_service.py)              │
│  - 목록 조회 로직                                 │
│  - 정렬 및 페이징                                 │
│  - Langfuse 추적                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ├──────────────┬─────────────────┐
                 ▼              ▼                 ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
│  ChromaDBService │  │ AuthService  │  │ Langfuse     │
│  (기존)           │  │ (기존)        │  │ (기존)        │
└──────────────────┘  └──────────────┘  └──────────────┘
```

## 🚀 빠른 시작

### 1단계: 브랜치 확인

```bash
# 현재 브랜치 확인
git branch
# * 001-admin-qa-list

# 최신 스펙 확인
ls specs/001-admin-qa-list/
# spec.md  plan.md  research.md  data-model.md  contracts/  quickstart.md
```

### 2단계: 데이터 마이그레이션 (필요 시)

기존 ChromaDB 데이터에 `created_at` 메타데이터가 없다면:

```bash
# 마이그레이션 스크립트 실행
python scripts/migrate_add_created_at.py
```

또는 개발용으로 테스트 데이터 생성:

```python
# scripts/generate_test_data.py
from datetime import datetime, timedelta
from src.services.chromadb_service import ChromaDBService
from src.models.qa_item import QAItem

service = ChromaDBService()

# 30개의 테스트 데이터 생성
for i in range(30):
    timestamp = datetime.now() - timedelta(hours=i)
    item = QAItem(
        question=f"테스트 질문 {i+1}",
        answer=f"테스트 답변 {i+1}",
        metadata={"created_at": timestamp.isoformat()}
    )
    service.add_qa_items([item])

print("✅ 30개의 테스트 데이터 생성 완료")
```

```bash
python scripts/generate_test_data.py
```

### 3단계: 모델 생성

**파일**: `src/models/qa_list_models.py`

```python
"""QA 목록 조회용 데이터 모델"""
from dataclasses import dataclass
from typing import Optional, List
import math

@dataclass
class QAListItem:
    question: str
    answer: str
    id: str
    created_at: str
    metadata: Optional[dict] = None
    
    @classmethod
    def from_chromadb_result(cls, doc: str, metadata: dict, id: str):
        return cls(
            question=doc,
            answer=metadata.get("answer", ""),
            id=id,
            created_at=metadata.get("created_at", "2000-01-01T00:00:00"),
            metadata=metadata
        )

@dataclass
class PaginationState:
    current_page: int = 1
    total_pages: int = 1
    items_per_page: int = 10
    total_items: int = 0
    
    def __post_init__(self):
        if self.total_items > 0:
            self.total_pages = math.ceil(self.total_items / self.items_per_page)
        else:
            self.total_pages = 1
    
    def get_offset(self) -> int:
        return (self.current_page - 1) * self.items_per_page
```

**테스트 실행**:

```bash
pytest tests/unit/test_qa_list_models.py -v
```

### 4단계: 서비스 생성

**파일**: `src/services/qa_list_service.py`

```python
"""QA 목록 조회 서비스"""
from typing import List, Tuple
from src.models.qa_list_models import QAListItem, PaginationState
from src.services.chromadb_service import get_chromadb_service
from src.services.langfuse_service import get_langfuse_service
import logging

logger = logging.getLogger(__name__)

class QAListService:
    def __init__(self):
        self.chromadb = get_chromadb_service()
        self.langfuse = get_langfuse_service()
    
    def list_items(self, page: int = 1, items_per_page: int = 10) -> Tuple[List[QAListItem], PaginationState]:
        """목록 조회 (Langfuse 추적 포함)"""
        trace = self.langfuse.trace(
            name="admin_list_qa_items",
            input={"page": page, "items_per_page": items_per_page}
        )
        
        try:
            # 1. ChromaDB에서 전체 조회
            with trace.span(name="chromadb_get_all") as span:
                results = self.chromadb.collection.get(
                    include=["documents", "metadatas"]
                )
                span.update(output={"count": len(results["ids"])})
            
            # 2. QAListItem으로 변환
            items = [
                QAListItem.from_chromadb_result(doc, meta, id)
                for doc, meta, id in zip(
                    results["documents"],
                    results["metadatas"],
                    results["ids"]
                )
            ]
            
            # 3. 최신 등록순 정렬
            with trace.span(name="sort_items"):
                sorted_items = sorted(
                    items,
                    key=lambda x: x.created_at,
                    reverse=True
                )
            
            # 4. 페이징
            pagination = PaginationState(
                current_page=page,
                items_per_page=items_per_page,
                total_items=len(sorted_items)
            )
            
            offset = pagination.get_offset()
            page_items = sorted_items[offset:offset + items_per_page]
            
            trace.update(output={"success": True, "returned": len(page_items)})
            return page_items, pagination
            
        except Exception as e:
            trace.update(output={"success": False, "error": str(e)}, level="ERROR")
            raise

# 싱글톤
_instance = None

def get_qa_list_service() -> QAListService:
    global _instance
    if _instance is None:
        _instance = QAListService()
    return _instance
```

**테스트 실행**:

```bash
pytest tests/integration/test_admin_list.py -v
```

### 5단계: UI 컴포넌트 생성

**파일**: `src/ui/admin_list_tab.py`

```python
"""관리자 목록 조회 UI 컴포넌트"""
import gradio as gr
from src.services.qa_list_service import get_qa_list_service

def render_qa_cards(items) -> str:
    """QA 항목들을 카드 형식 HTML로 렌더링"""
    if not items:
        return '<div style="text-align: center; padding: 40px; color: #666;">등록된 질문답변이 없습니다</div>'
    
    html = '<div style="display: flex; flex-direction: column; gap: 16px;">'
    for item in items:
        html += f'''
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; 
                    background: #f9f9f9; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 12px;">
                <strong style="color: #2563eb;">질문:</strong>
                <div style="max-height: 150px; overflow-y: auto; margin-top: 8px;
                            padding: 8px; background: white; border-radius: 4px;">
                    {item.question}
                </div>
            </div>
            <div>
                <strong style="color: #059669;">답변:</strong>
                <div style="max-height: 200px; overflow-y: auto; margin-top: 8px;
                            padding: 8px; background: white; border-radius: 4px;">
                    {item.answer}
                </div>
            </div>
        </div>
        '''
    html += '</div>'
    return html

def create_admin_list_tab():
    """관리자 목록 조회 탭 생성"""
    service = get_qa_list_service()
    
    with gr.Tab("목록 조회"):
        gr.Markdown("## 등록된 질문답변 목록")
        
        # 상태
        current_page = gr.State(1)
        items_per_page = gr.State(10)
        
        # 컨트롤
        with gr.Row():
            refresh_btn = gr.Button("🔄 새로고침", variant="secondary")
            items_selector = gr.Dropdown(
                choices=[10, 20, 50],
                value=10,
                label="페이지당 항목 수"
            )
        
        # 목록
        qa_list = gr.HTML()
        
        # 페이징
        with gr.Row():
            prev_btn = gr.Button("◀ 이전")
            page_info = gr.Markdown("페이지 1/1")
            next_btn = gr.Button("다음 ▶")
        
        total_items = gr.Markdown("총 0개의 항목")
        
        # 로드 함수
        def load_list(page, per_page):
            items, pagination = service.list_items(page, per_page)
            return (
                render_qa_cards(items),
                pagination.get_page_info_text(),
                pagination.get_total_items_text(),
                page
            )
        
        # 초기 로드
        qa_list.value, page_info.value, total_items.value, current_page.value = load_list(1, 10)
        
        # 이벤트 핸들러
        refresh_btn.click(
            fn=load_list,
            inputs=[current_page, items_per_page],
            outputs=[qa_list, page_info, total_items, current_page]
        )
        
        return qa_list, page_info, total_items
```

### 6단계: main.py에 통합

**파일**: `src/main.py`

```python
# 기존 import에 추가
from src.ui.admin_list_tab import create_admin_list_tab

# create_interface() 메서드 내 관리자 탭에 추가
with gr.Tab("관리자"):
    # ... 기존 로그인 코드 ...
    
    # 관리자 기능 탭들
    with gr.Tabs(visible=False) as admin_tabs:  # 로그인 후 표시
        # 기존 "Q&A 관리" 탭
        with gr.Tab("Q&A 관리"):
            # ... 기존 코드 ...
        
        # 새로운 "목록 조회" 탭
        create_admin_list_tab()
```

### 7단계: 앱 실행 및 테스트

```bash
# 앱 실행
python src/main.py

# 브라우저에서 http://localhost:7860 열기
# 1. 관리자 탭으로 이동
# 2. 패스워드 입력 (기본값: 1234)
# 3. "목록 조회" 탭 클릭
# 4. 카드 형식으로 표시된 목록 확인
```

## 🧪 테스트 실행

### 전체 테스트

```bash
# 모든 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=src --cov-report=html
```

### 단위 테스트만

```bash
pytest tests/unit/test_qa_list_models.py -v
pytest tests/unit/test_qa_list_service.py -v
```

### 통합 테스트만

```bash
pytest tests/integration/test_admin_list.py -v
```

## 🐛 디버깅 팁

### Langfuse 추적 확인

```bash
# Langfuse 대시보드에서 확인
# https://cloud.langfuse.com 또는 설정된 LANGFUSE_HOST

# 추적 이름: "admin_list_qa_items"
# 예상 spans: chromadb_get_all, sort_items, paginate
```

### 로그 확인

```python
# src/services/qa_list_service.py에 추가
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Retrieved {len(items)} items from ChromaDB")
logger.debug(f"Pagination: page={page}, total_pages={pagination.total_pages}")
```

### ChromaDB 데이터 확인

```python
# Python REPL에서
from src.services.chromadb_service import get_chromadb_service

service = get_chromadb_service()
results = service.collection.get(include=["documents", "metadatas"])

print(f"Total items: {len(results['ids'])}")
print(f"First item: {results['documents'][0]}")
print(f"First metadata: {results['metadatas'][0]}")
```

## 📚 참고 문서

- **스펙**: [spec.md](spec.md) - 기능 명세
- **계획**: [plan.md](plan.md) - 구현 계획
- **연구**: [research.md](research.md) - 기술 결정 사항
- **데이터 모델**: [data-model.md](data-model.md) - 모델 정의
- **계약**: [contracts/README.md](contracts/README.md) - 계약 설명

## 🎓 다음 학습 내용

1. **테스트 추가**: 엣지 케이스 테스트 작성
2. **성능 최적화**: 대량 데이터 환경에서 페이징 최적화
3. **UI 개선**: 카드 디자인 커스터마이징
4. **에러 처리**: 더 세밀한 오류 메시지

## ❓ 문제 해결

### 문제: "created_at이 없습니다" 오류

```bash
# 마이그레이션 실행
python scripts/migrate_add_created_at.py
```

### 문제: 목록이 비어 있음

```python
# ChromaDB에 데이터가 있는지 확인
from src.services.chromadb_service import get_chromadb_service
service = get_chromadb_service()
print(service.collection.count())  # 0이면 데이터 없음

# 테스트 데이터 생성
python scripts/generate_test_data.py
```

### 문제: 페이징이 작동하지 않음

```python
# PaginationState 검증
from src.models.qa_list_models import PaginationState
state = PaginationState(current_page=2, items_per_page=10, total_items=25)
print(state.get_offset())  # 10이어야 함
print(state.total_pages)   # 3이어야 함
```

## ✅ 체크리스트

구현 완료 체크리스트:

- [ ] `src/models/qa_list_models.py` 생성
- [ ] `src/services/qa_list_service.py` 생성
- [ ] `src/ui/admin_list_tab.py` 생성
- [ ] `src/main.py`에 통합
- [ ] 단위 테스트 작성 및 통과
- [ ] 통합 테스트 작성 및 통과
- [ ] Langfuse 추적 확인
- [ ] UI에서 수동 테스트
- [ ] 마이그레이션 스크립트 실행 (필요 시)
- [ ] 문서 업데이트

## 🚀 배포 준비

```bash
# 1. 모든 테스트 통과 확인
pytest tests/ -v

# 2. 코드 스타일 확인
black src/ tests/
flake8 src/ tests/

# 3. 타입 체크 (선택적)
mypy src/models/qa_list_models.py

# 4. 커밋
git add .
git commit -m "feat: 관리자 질문답변 목록 조회 기능 구현"

# 5. PR 생성
gh pr create --title "feat: 관리자 질문답변 목록 조회" --body "Closes #001"
```

---

**Happy Coding! 🎉**
