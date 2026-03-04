# 구현 계획: Q&A 항목 삭제 기능 (Feature 002)

**브랜치**: `002-delete-qa-item` | **날짜**: 2026-03-05 | **Spec**: [spec.md](spec.md)  
**입력**: `/specs/002-delete-qa-item/spec.md` 기반 기능 사양

**상태**: Phase 0 완료 → Phase 1 설계 진행 중

---

## 📋 요약

**요구사항**: 관리자 목록 조회 탭에서 각 Q&A 항목에 삭제 버튼을 추가하고, 클릭 시 확인 다이얼로그를 표시한 후 ChromaDB에서 항목을 삭제하며, 모든 작업을 Langfuse로 추적합니다.

**기술 접근**:
- **UI**: Gradio 카드 컴포넌트에 HTML 버튼 + JavaScript 이벤트
- **저장소**: ChromaDB `.delete(qa_id)` 메서드
- **상태 관리**: Gradio State + 숨겨진 트리거 버튼
- **관찰 가능성**: Langfuse span으로 삭제 생명주기 추적 (남은 작업 - FR-010)

---

## 🔧 기술 문맥

| 항목 | 값 |
|------|-----|
| **언어/버전** | Python 3.12 |
| **주요 의존성** | Gradio 4.x, ChromaDB 0.5+, Langfuse SDK |
| **저장소** | ChromaDB (벡터 + 메타데이터) |
| **테스팅** | pytest 9.0+, 43개 테스트 현재 모두 통과 |
| **대상 플랫폼** | Linux 서버 (Gradio 웹 UI) |
| **프로젝트 유형** | Web service / 대화형 UI |
| **성능 목표** | 삭제 완료 < 2초 (중소 데이터셋 ~100개 항목) |
| **제약사항** | 페이지당 50개 항목 고정, Langfuse API 키 미설정 시 조용히 스킵 |
| **규모** | MVP, 단일 관리자 역할, 한 개 조직 |

---

## ✅ 헌법 검증 (Constitution Check)

*게이트: Phase 0 이후 재검증 필수*

### 5가지 핵심 원칙 준수 현황

| 원칙 | 상태 | 세부사항 |
|------|------|--------|
| **I. 관찰 가능성 우선** | ⚠️ 부분 | logger.info() 기본 로깅 있음, Langfuse span 추적 필요 (FR-010) |
| **II. 벡터 인식 데이터 계약** | ✅ 준수 | Hash ID 기반 ChromaDB 계약 명시됨 (research.md Decision 1) |
| **III. 사용자 중심 UI** | ✅ 준수 | 확인 다이얼로그 + gr.Info/Error 토스트 + 명확한 메시지 |
| **IV. 테스트 주도 개발** | ✅ 준수 | 43개 테스트 통과, UI + 통합 테스트 포함 |
| **V. 버전 관리** | ✅ N/A | 삭제 기능은 API 계약 변경 없음 |

### 게이트 상태

- ✅ **기존 구현 검증**: UI, ChromaDB 삭제, 상태 관리 모두 검증됨
- ✅ **테스트 커버리지**: 43개 테스트 통과 (커버리지 > 80%)
- ⏳ **FR-010 (Langfuse span)**: Phase 1에서 추가 예정
- ✅ **기술 스택**: Gradio 4.x, ChromaDB 0.5+, pytest 모두 호환성 확인

**Gate 결과**: ✅ **Phase 1 진행 승인**

---

## 📁 프로젝트 구조

### 문서 (본 기능)

```text
specs/002-delete-qa-item/
├── spec.md              # 기능 사양 (User Story 4개, FR 10개)
├── plan.md              # 이 파일 (실행 계획)
├── research.md          # Phase 0 연구 결과 (Decision 5개)
├── data-model.md        # Phase 1 (예정) - 데이터 모델
├── quickstart.md        # Phase 1 (예정) - 빠른 시작
├── contracts/           # Phase 1 (예정) - 계약/인터페이스
└── tasks.md             # Phase 2 (예정) - 구체 작업 목록
```

### 소스코드 (저장소 루트)

```text
src/
├── models/
│   ├── qa_delete_models.py      # QADeleteRequest, Result 모델
│   └── qa_list_models.py        # QAListItem 모델
├── services/
│   ├── qa_delete_service.py     # 삭제 비즈니스 로직 (싱글톤)
│   ├── chromadb_service.py      # ChromaDB 작업 (+ FR-010 예정)
│   ├── langfuse_service.py      # Langfuse 통합 (+ FR-010 예정)
│   └── qa_list_service.py       # 목록 조회 서비스
└── ui/
    └── admin_list_tab.py        # 관리자 UI (Gradio)

tests/
├── unit/
│   └── test_admin_list_tab.py   # UI 테스트
├── integration/
│   └── test_qa_update.py        # 삭제 통합 테스트
├── contract/
│   └── test_chromadb_contract.py # 데이터 계약 테스트
└── performance/
    └── test_concurrent_users.py # 동시 삭제 테스트
```

---

## 🎯 Phase 1 설계 작업 (30-55분 예정)

### Task 1: Langfuse Span 통합 (FR-010)
**목표**: 모든 삭제 작업을 Langfuse로 추적 가능하게

```python
# 패턴
with langfuse_client.trace(
    name="delete_qa_item",
    input={"qa_id": qa_id, "admin_user": admin_user},
) as trace:
    result = delete_service.delete(qa_id)  # Request 생명주기
    trace.output = {"success": result.success, "message": result.message}
    trace.metadata = {"timestamp": datetime.now()}
```

**파일**: `src/services/qa_delete_service.py`, `src/services/langfuse_service.py`

**테스트**: `test_delete_qa_item_langfuse_span` 추가

### Task 2: Data Model 문서화
**목표**: `data-model.md` 작성

- QADeleteRequest 엔티티
- QADeleteResult 엔티티
- ChromaDB ID 계약

### Task 3: 계약 (Contracts) 작성
**목표**: `contracts/chromadb-delete.md` 작성

```yaml
Operation: delete_qa_item
Input:
  - qa_id: str (Hash-based, immutable)
  - admin_user: str (audit trail)
Output:
  - success: bool
  - message: str
  - error_reason?: str
Preconditions:
  - qa_id must exist in ChromaDB
Postconditions:
  - Item deleted from collection
  - List auto-refreshed
```

### Task 4: 빠른 시작 (Quickstart)
**목표**: `quickstart.md` 작성

```markdown
### 삭제 기능 사용
1. 관리자 로그인 → 📋 목록 조회
2. 각 카드의 🗑️ 삭제 버튼 클릭
3. 확인 다이얼로그 → "예" 선택
4. Langfuse 대시보드에서 추적 확인
```

---

## 🧪 테스트 전략 (이미 구현됨)

| 테스트 유형 | 파일 | 상태 | 커버리지 |
|-----------|------|------|---------|
| 유닛 테스트 | `test_admin_list_tab.py` | ✅ 2개 통과 | 삭제 버튼 HTML, 빈 목록 처리 |
| 통합 테스트 | `test_qa_update.py` | ✅ 5개 통과 | 삭제 플로우 엔드-투-엔드 |
| 계약 테스트 | `test_chromadb_contract.py` | ✅ 16개 통과 | ChromaDB 인터페이스 |
| 동시성 테스트 | `test_concurrent_users.py` | ✅ 통과 | 2명 관리자 동시 삭제 |

### Phase 1 추가 테스트

```python
def test_delete_qa_item_langfuse_span():
    """Langfuse span이 생성되고 메타데이터가 기록됨"""
    # Arrange: Mock Langfuse client
    # Act: delete_qa_item() 호출
    # Assert: trace.name == "delete_qa_item", metadata 포함
```

---

## 📊 구현 현황

```
총 요구사항: 10개 (FR-001 ~ FR-010)
완료: 9개 (90%)
┌─────────────────────────────────────┐
│ ██████████████████░░░░░░ 90% (9/10) │
└─────────────────────────────────────┘

남은 작업:
- FR-010: Langfuse span 추적 (1개, 10%)
  예상 시간: 30-40분
  테스트: 10-15분
  총: 40-55분
```

---

## 🚀 Phase 1 입장 조건

**✅ 모두 만족**:

- [x] Spec 명확함 (User Story 4개, FR 10개 정의)
- [x] 기존 구현 검증됨 (9개 요구사항 구현 및 테스트 완료)
- [x] 기술 스택 결정됨 (Python 3.12, Gradio 4.x, ChromaDB, Langfuse)
- [x] 헌법 원칙 검증됨 (5가지 원칙 중 4가지 준수, 1가지 부분 준수)
- [x] 통합 패턴 결정됨 (Langfuse span 기반)
- [x] 테스트 작성 가능함 (43개 테스트 현재 통과)

**→ Phase 1 진행 권장** ✅

---

## 🔍 알려진 이슈

| ID | 제목 | 상태 | Phase |
|----|------|------|-------|
| 001 | Langfuse API 키 미설정 시 span 스킵 | ℹ️ 예상 동작 | 1 |
| 002 | 페이지당 50개 고정 | ℹ️ 요구사항 | 1 |
| 003 | 동시 삭제 시 "항목 없음" 오류 | ✅ 테스트 완료 | 2 |


