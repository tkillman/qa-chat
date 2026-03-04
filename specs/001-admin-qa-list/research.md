# Research: 관리자 질문답변 목록 조회

**Feature**: 001-admin-qa-list  
**Date**: 2026-03-05  
**Phase**: Phase 0 - Research & Technical Discovery

## 목적

이 문서는 관리자 질문답변 목록 조회 기능을 구현하기 위한 기술적 연구와 결정 사항을 기록합니다. Technical Context의 NEEDS CLARIFICATION 항목을 해결하고 구현에 필요한 모든 기술적 정보를 제공합니다.

## 연구 주제

### 1. ChromaDB 전체 항목 조회 방법

#### 결정: `collection.get()` 메서드 사용

**근거**:
- ChromaDB의 `collection.get()` 메서드는 벡터 검색 없이 메타데이터 조회 가능
- 기존 `search_similar()` 메서드와 다르게 전체 항목 조회 지원
- ID 지정 없이 호출하면 전체 컬렉션 조회 가능

**구현 방식**:
```python
# ChromaDBService에 새 메서드 추가
def get_all_items(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
    """ChromaDB에서 모든 항목 조회 (페이징 지원)
    
    Args:
        limit: 반환할 최대 항목 수 (None이면 전체)
        offset: 시작 인덱스 (페이징용)
        
    Returns:
        [{"question": str, "answer": str, "id": str}, ...]
    """
    results = self.collection.get(
        limit=limit,
        offset=offset,
        include=["documents", "metadatas"]
    )
    # documents는 질문, metadatas["answer"]는 답변
    return results
```

**대안 평가**:
- ❌ `query()` 사용: 불필요한 벡터 검색 수행, 성능 낭비
- ❌ 직접 DB 접근: ChromaDB는 추상화를 통해서만 접근해야 함
- ✅ `get()` 메서드: 가장 단순하고 효율적

**참고 문서**:
- ChromaDB 공식 문서: https://docs.trychroma.com/reference/py-collection#get
- 기존 코드: `src/services/chromadb_service.py` (add, query 패턴 참고)

---

### 2. Gradio 페이징 UI 패턴

#### 결정: State + Button + Number 조합

**근거**:
- Gradio는 상태 관리를 `gr.State()` 컴포넌트로 지원
- 페이지 전환은 버튼 클릭 이벤트로 처리
- 현재 페이지 표시는 `gr.Markdown()` 또는 `gr.Number()`로 처리

**구현 방식**:
```python
with gr.Tab("관리자"):
    with gr.Tab("목록 조회"):
        # 상태 관리
        current_page = gr.State(1)
        items_per_page = gr.State(10)
        
        # 페이징 컨트롤
        with gr.Row():
            prev_btn = gr.Button("◀ 이전")
            page_info = gr.Markdown("페이지 1/1")
            next_btn = gr.Button("다음 ▶")
        
        # 항목 수 선택
        items_selector = gr.Dropdown(
            choices=[10, 20, 50],
            value=10,
            label="페이지당 항목 수"
        )
        
        # 목록 표시 영역
        qa_list = gr.HTML()  # 카드 형식 HTML 렌더링
        
        # 이벤트 핸들러
        prev_btn.click(
            fn=handle_prev_page,
            inputs=[current_page, items_per_page],
            outputs=[current_page, qa_list, page_info]
        )
```

**대안 평가**:
- ❌ 외부 JavaScript: Gradio는 순수 Python만 사용하는 것이 헌법 원칙
- ❌ Dataframe 컴포넌트: 카드 형식 레이아웃 불가능, 스크롤 제어 어려움
- ✅ HTML + State: 커스텀 레이아웃 가능, 상태 관리 명확

**참고 문서**:
- Gradio State 문서: https://www.gradio.app/docs/state
- 기존 코드: `src/main.py` (admin 탭의 상태 관리 패턴 참고)

---

### 3. 카드 레이아웃 구현

#### 결정: `gr.HTML()` 컴포넌트로 커스텀 HTML/CSS

**근거**:
- Gradio의 기본 컴포넌트는 카드 레이아웃을 직접 지원하지 않음
- `gr.HTML()`은 커스텀 HTML/CSS를 렌더링할 수 있음
- 스크롤 박스는 CSS `overflow-y: auto` 속성으로 구현

**구현 방식**:
```python
def render_qa_cards(items: List[Dict]) -> str:
    """QA 항목들을 카드 형식 HTML로 렌더링
    
    Args:
        items: [{"question": str, "answer": str}, ...]
        
    Returns:
        HTML 문자열
    """
    html = '<div style="display: flex; flex-direction: column; gap: 16px;">'
    
    for item in items:
        html += f'''
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; 
                    background: #f9f9f9; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 12px;">
                <strong style="color: #2563eb;">질문:</strong>
                <div style="max-height: 150px; overflow-y: auto; margin-top: 8px;
                            padding: 8px; background: white; border-radius: 4px;">
                    {item["question"]}
                </div>
            </div>
            <div>
                <strong style="color: #059669;">답변:</strong>
                <div style="max-height: 200px; overflow-y: auto; margin-top: 8px;
                            padding: 8px; background: white; border-radius: 4px;">
                    {item["answer"]}
                </div>
            </div>
        </div>
        '''
    
    html += '</div>'
    return html
```

**대안 평가**:
- ❌ `gr.Accordion()`: 한 번에 하나만 열림, 카드 레이아웃 아님
- ❌ `gr.Textbox()` 반복: 레이아웃 제어 어려움, 시각적 구분 약함
- ✅ `gr.HTML()`: 완전한 커스터마이징 가능, CSS 스타일 적용 가능

**스타일 가이드**:
- 카드 간격: 16px
- 카드 패딩: 16px
- 질문 최대 높이: 150px (스크롤)
- 답변 최대 높이: 200px (스크롤)
- 색상: 질문(파랑 #2563eb), 답변(초록 #059669)

---

### 4. 정렬 로직 (최신 등록순)

#### 결정: 타임스탬프 메타데이터 추가 + Python 정렬

**근거**:
- ChromaDB는 기본적으로 삽입 순서를 보장하지 않음
- 메타데이터에 타임스탬프를 추가하여 정렬 기준 확보
- Python에서 `sorted()` 함수로 정렬 (간단하고 명확)

**구현 방식**:
```python
# 1. QA 항목 추가 시 타임스탬프 포함 (기존 코드 수정 필요)
from datetime import datetime

def add_qa_item_with_timestamp(question: str, answer: str):
    metadata = {
        "answer": answer,
        "created_at": datetime.now().isoformat()  # ISO 8601 형식
    }
    # ChromaDB에 추가...

# 2. 목록 조회 시 정렬
def get_sorted_items(items: List[Dict]) -> List[Dict]:
    """최신 등록순(내림차순)으로 정렬
    
    Args:
        items: ChromaDB에서 조회한 항목들
        
    Returns:
        정렬된 항목 리스트
    """
    return sorted(
        items,
        key=lambda x: x.get("metadata", {}).get("created_at", ""),
        reverse=True  # 내림차순 (최신이 먼저)
    )
```

**마이그레이션 고려사항**:
- 기존 데이터에는 `created_at` 없음
- 마이그레이션 스크립트로 기존 항목에 현재 시간 추가
- 또는 `created_at` 없는 항목은 오래된 것으로 간주

**대안 평가**:
- ❌ ChromaDB 내부 순서 의존: 보장되지 않음
- ❌ 파일 수정 시간 사용: init.txt 재로딩 시 변경됨
- ✅ 타임스탬프 메타데이터: 명시적이고 신뢰 가능

---

### 5. Langfuse 추적 통합

#### 결정: 목록 조회 작업을 독립적인 Trace로 추적

**근거**:
- 헌법 I: 모든 주요 작업은 Langfuse로 추적해야 함
- 목록 조회는 사용자 상호작용이므로 독립적인 trace 필요
- 성능 지표 (로딩 시간, 항목 수) 기록 필수

**구현 방식**:
```python
from src.services.langfuse_service import get_langfuse_service

def list_qa_items_with_tracing(page: int, items_per_page: int) -> tuple:
    """목록 조회 (Langfuse 추적 포함)
    
    Returns:
        (items, total_count, duration_ms)
    """
    langfuse = get_langfuse_service()
    
    # Trace 시작
    trace = langfuse.trace(
        name="admin_list_qa_items",
        input={
            "page": page,
            "items_per_page": items_per_page
        }
    )
    
    try:
        # Span 1: ChromaDB 조회
        with trace.span(name="chromadb_get_all") as span:
            items = chromadb_service.get_all_items()
            span.update(
                output={"count": len(items)},
                metadata={"operation": "list"}
            )
        
        # Span 2: 정렬
        with trace.span(name="sort_items") as span:
            sorted_items = sort_by_timestamp(items)
        
        # Span 3: 페이징
        with trace.span(name="paginate") as span:
            paginated = paginate_items(sorted_items, page, items_per_page)
            span.update(
                output={"returned_count": len(paginated)},
                metadata={"page": page, "items_per_page": items_per_page}
            )
        
        # Trace 완료
        trace.update(
            output={"success": True, "total_items": len(items)},
            metadata={"duration_ms": trace.get_duration()}
        )
        
        return paginated, len(items), trace.get_duration()
        
    except Exception as e:
        trace.update(
            output={"success": False, "error": str(e)},
            level="ERROR"
        )
        raise
```

**추적 지표**:
- 입력: page, items_per_page
- 출력: 반환된 항목 수, 전체 항목 수
- 지연시간: ChromaDB 조회, 정렬, 페이징 각 단계
- 오류: 예외 발생 시 스택 트레이스

**대안 평가**:
- ❌ 추적 없음: 헌법 위반
- ❌ 단일 Span만: 세부 성능 파악 불가
- ✅ Trace + 다중 Span: 단계별 성능 분석 가능

**참고 코드**:
- 기존 Langfuse 패턴: `src/services/user_search_service.py`, `qa_update_service.py`

---

### 6. 새로고침 메커니즘

#### 결정: 수동 새로고침 버튼 + 이벤트 핸들러

**근거**:
- Clarification: 수동 새로고침 버튼 제공 (자동 새로고침 제외)
- Gradio 버튼 클릭으로 데이터 재조회 트리거
- 현재 페이지 상태 유지하면서 데이터만 새로고침

**구현 방식**:
```python
# UI 컴포넌트
with gr.Row():
    refresh_btn = gr.Button("🔄 새로고침", variant="secondary")
    total_items = gr.Markdown("총 0개의 항목")

# 이벤트 핸들러
def refresh_list(current_page: int, items_per_page: int):
    """목록 새로고침
    
    현재 페이지를 유지하면서 ChromaDB에서 최신 데이터 조회
    """
    items, total_count, _ = list_qa_items_with_tracing(current_page, items_per_page)
    cards_html = render_qa_cards(items)
    total_pages = math.ceil(total_count / items_per_page)
    page_info = f"페이지 {current_page}/{total_pages}"
    total_info = f"총 {total_count}개의 항목"
    
    return cards_html, page_info, total_info

refresh_btn.click(
    fn=refresh_list,
    inputs=[current_page, items_per_page],
    outputs=[qa_list, page_info, total_items]
)
```

**사용자 경험**:
- 버튼 클릭 시 즉시 데이터 재조회
- 현재 페이지 유지 (페이지 1로 돌아가지 않음)
- 로딩 표시 (Gradio 기본 제공)

---

### 7. 빈 목록 처리

#### 결정: 조건부 렌더링

**근거**:
- Clarification: 항목이 없으면 페이징 요소 모두 숨김
- "등록된 질문답변이 없습니다" 메시지만 표시
- Gradio의 `visible` 속성으로 동적 제어

**구현 방식**:
```python
def handle_empty_list():
    """빈 목록 처리
    
    Returns:
        (cards_html, page_controls_visible, message)
    """
    message = "등록된 질문답변이 없습니다"
    empty_html = f'<div style="text-align: center; padding: 40px; color: #666;">{message}</div>'
    
    return (
        empty_html,           # qa_list
        False,                # prev_btn visible
        False,                # next_btn visible
        False,                # page_info visible
        False,                # items_selector visible
        True,                 # empty_message visible
        "총 0개의 항목"       # total_items
    )

def render_list_view(items: List[Dict], page: int, items_per_page: int):
    """목록 뷰 렌더링 (빈 목록 처리 포함)"""
    if not items:
        return handle_empty_list()
    
    # 정상 렌더링...
    return (
        render_qa_cards(items),
        True,  # 페이징 컨트롤 표시
        True,
        True,
        True,
        False, # 빈 메시지 숨김
        f"총 {len(items)}개의 항목"
    )
```

---

## 기술 결정 요약

| 주제 | 결정 | 근거 |
|------|------|------|
| ChromaDB 조회 | `collection.get()` | 벡터 검색 불필요, 효율적 |
| 페이징 UI | State + Button + HTML | Gradio 표준 패턴, 유연함 |
| 카드 레이아웃 | `gr.HTML()` + CSS | 커스텀 레이아웃 필요 |
| 정렬 | 타임스탬프 메타데이터 | 명시적이고 신뢰 가능 |
| 추적 | Langfuse Trace + Spans | 헌법 준수, 성능 분석 |
| 새로고침 | 수동 버튼 | Clarification 결정 |
| 빈 목록 | 조건부 렌더링 | UX 명확성 |

## 구현 우선순위

**Phase 1 (핵심 기능)**:
1. ChromaDBService에 `get_all_items()` 추가
2. QAListService 생성 (페이징, 정렬 로직)
3. 기본 UI 구조 (카드 없이 텍스트만)
4. Langfuse 추적 통합

**Phase 2 (UI 개선)**:
5. 카드 레이아웃 HTML/CSS
6. 페이징 컨트롤 (이전/다음 버튼)
7. 페이지당 항목 수 선택

**Phase 3 (추가 기능)**:
8. 새로고침 버튼
9. 총 항목 수 표시
10. 빈 목록 처리

## 마이그레이션 요구사항

### 기존 데이터에 타임스탬프 추가

```python
# 마이그레이션 스크립트 (한 번만 실행)
def migrate_add_timestamps():
    """기존 QA 항목에 created_at 메타데이터 추가"""
    from datetime import datetime
    
    chromadb_service = ChromaDBService()
    items = chromadb_service.get_all_items()
    
    for i, item in enumerate(items):
        if "created_at" not in item.get("metadata", {}):
            # 역순으로 타임스탬프 할당 (오래된 항목에 더 이른 시간)
            timestamp = datetime(2026, 1, 1) + timedelta(minutes=i)
            item["metadata"]["created_at"] = timestamp.isoformat()
            # 업데이트...
```

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 전략 |
|--------|------|-----------|
| 대량 데이터 로딩 느림 | 성능 | 페이징으로 제한, 필요 시 캐싱 |
| 타임스탬프 없는 기존 데이터 | 정렬 오류 | 마이그레이션 스크립트 실행 |
| HTML 렌더링 보안 | XSS | HTML 이스케이프 처리 |
| 동시 접속 시 상태 충돌 | 데이터 불일치 | 새로고침 버튼으로 해결 |

## 다음 단계

이제 Phase 1: 데이터 모델 및 계약 설계로 진행합니다.
- `data-model.md`: PaginationState, QAListItem 모델 정의
- `contracts/`: (없음 - 읽기 전용이므로 새 계약 불필요)
- `quickstart.md`: 개발자를 위한 빠른 시작 가이드
