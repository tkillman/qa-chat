# 구현 계획: Q&A 항목 삭제 기능

**브랜치**: `002-delete-qa-item` | **날짜**: 2026-03-05 | **사양**: [spec.md](spec.md)  
**상태**: 계획 단계 (모든 모호함 해결됨, 설계 준비 완료)

## 요약

Q&A Chat 기존 기능에 **항목 삭제** 능력 추가:
- **US1 - 삭제 버튼 표시** (P1): 목록 조회 카드의 title/header 우측에 ���️ 버튼 표시
- **US2 - 확인 다이얼로그** (P1): 삭제 버튼 클릭 시 확인 모달 표시
- **US3 - 항목 삭제 실행** (P1): 다이얼로그 "예" 클릭 시 ChromaDB에서 삭제 + 목록 갱신
- **US4 - 상태 메시지** (P2): 진행 중/완료/실패 상태를 toast 알림으로 표시

**기술 접근법**: Gradio UI (다이얼로그 + 비활성화) + ChromaDB 삭제 API + Langfuse 추적

**기존 기능 재사용**:
- `QAListService.list_items()` - 목록 조회 (Feature 001)
- `admin_list_tab.py` - UI 카드 렌더링 (Feature 001)
- ChromaDB singleton (`get_chromadb_service()`)
- Langfuse 계측 패턴

---

## 기술 컨텍스트

**언어/버전**: Python 3.12 ✅  
**주요 의존성**: Gradio 4.26+, ChromaDB 0.5+, Langfuse 2.12+ ✅  
**저장소**: 결정 |
|---------|------|------|
| 단일 관리자 세션 제약 | 설계에 포함됨 | Optimistic 동시성 (EC-002 처리) |
| 네트워크 오류 처리 | 설계에 포함됨 | 재시도 옵션 제공 (EC-003) |
| Langfuse 불가 흐름 | 설계에 포함됨 | 삭제는 계속 진행 (Assumption) |

---

## Phase 별 산출물

### Phase 0 - 연구 ✅ (명확화 완료)

**해결된 모든 불명확함**:
```
✅ Q1: Q&A 항목 식별 = Hash ID (get_hash_key())
✅ Q2: 버튼 배치 = Title/Header 우측 embedded
✅ Q3: 메시지 표시 = Toast 알림 (gr.Info/Error, 3초)
✅ Q4: 권한 검증 = 관리자 인증만 (재인증 불필요)
✅ Q5: 동시성 = Optimistic (먼저 성공, 두 번째는 오류)
```

**산출물**: [research.md](research.md) (작성 준비 완료)

### Phase 1 - 설계 (이 명령어의 산출물)

**생성될 문서**:
- [data-model.md](data-model.md) - QADeleteRequest, QADeleteResult 엔티티
- [quickstart.md](quickstart.md) - 로컬 테스트 가이드
- [contracts/](contracts/) - ChromaDB 삭제 계약

**생성될 코드**:
- `src/models/qa_delete_models.py` - 2개 dataclass
- `src/services/qa_delete_service.py` - 로직 서비스

### Phase 2 - 구현 (예정)

**명령어**: `/speckit.tasks`
e 1 (셋업 가이드)
├── spec.md                  # 사양서 (4가지 User Story)
├── contracts/               # 인터페이스 계약
└── checklists/
    └── requirements.md      # 추적 가능성 매트릭스
```

### 소스 코드 레이아웃 (Phase 1-2 대기)

```
src/
├── models/
│   └── qa_delete_models.py          # NEW: QADeleteRequest, QADeleteResult
├── services/
│   ├── qa_delete_service.py         # NEW: delete_qa_item() 로직
│   ├── qa_list_service.py           # 기존 (재사용: list_items())
│   └── langfuse_service.py          # 기존 (재사용: span 기록)
└── ui/
    └── admin_list_tab.py            # 수정: 삭제 버튼 + 다이얼로그 추가

tests/
├── unit/
│   └── test_qa_delete_service.py    # NEW: delete_qa_item() 단위 테스트
├── integration/
│   └── test_admin_delete_flow.py    # NEW: 전체 삭제 흐름
└── contract/
    └── test_chromadb_delete.py      # NEW: ChromaDB 계약 테스트
```

### Feature 001과의 의존성

| 기존 컴포넌트 | 재사용 방식 |
|-----------|----------|
| `QAListService.list_items()` | 삭제 후 목록 새로고침에 사용동작
4. Edge case 테스트: EC-001 ~ EC-007 (동시성, 네트워크, 빈 목록)

---

## 프로젝트 구조

### 문서 산출물 (Phase 0-1)

```
specs/002-delete-qa-item/
├── plan.md                  # 이 파일
├── research.md              # Phase 0 (모든 기술 결정 기록)
├── data-model.md            # Phase 1 (엔티티 정의)
├── quickstart.md            # Phas |
| `admin_list_tab.py` | UI 카드에 삭제 버튼 추가 |
| `ChromaDBService` (singleton) | 삭제 작업에 직접 사용 |
| `LangfuseService` | 삭제 이벤트 span 기록 |
| `models/qa_item.py` | QAItem.get_hash_key() 식별자 사용 |
| `src/main.py` | 기존 admin tab 통합, 콜백 연결 |

---

## 복잡도 추적

**헌법 위반**: 없음 ✅

| 잠재적 문제 | 상태 |- tasks.md 자동 생성 (구현 체크리스트)
- User Story별 작업 분해 (~15-20 작업)
- 예상 시간: 2-3 시간 (개발 + 테스트 + 통합)

---

## 기술 결정 기록

| 결정 | 선택지 | 선택 | 이유 |
|------|-------|------|-----|
| 식별자 방식 | Hash ID / UUID | Hash ID | Feature 001과 일관성, 기존 메타데이터 활용 |
| UI 배치 | 상단 / 하단 / 호버 | Title 우측 | 항상 보임, 스캔 시 자연스러움 |
| 상태 표시 | Toast / 모달 / 인라인 |) 재조회
- 실패 케이스: 예외 발생 시 사용자 오류 메시지 (FR-007)
- 장점: 데이터 일관성 보장 (SC-004 ✅)

**미적용 사항**: 임베딩 모델 설정은 Feature 001에서 이미 정의됨 (재사용)

### III. 사용자 중심 UI ✅

**준수**: Gradio 컴포넌트로 전체 구현
- 입력 검증: 다이얼로그 버튼 클릭만 유효 입력 (중복 클릭 방지 EC-007)
- 상태 관리: gr.State() 사용, 고아 요청 없음
- 피드백: Toast 알림 (gr.Info/Error) 자동 소멸
- 접근성: 버튼 라벨 명확 ("삭제" 아이콘 + 텍스트)
- 장점: UX 분명성 (SC-001 ✅, SC-002 ✅)

### IV. 테스트 주도 개발 (필수) ✅

**준수**: 4개 User Story에 대한 테스트 포함 계획
1. 단위 테스트: `QADeleteService.delete_qa_item()` (ChromaDB 모의)
2. 통합 테스트: 삭제 후 목록 갱신 흐름 (실제 ChromaDB)
3. UI 테스트: 다이얼로그 표시 및 버튼  Toast | 비차단적, Gradio 기본 지원 |
| 권한 검증 | 인증만 / 재인증 / Role | 인증만 | UX 최적화, 이미 로그인 상태 |
| 동시성 | Optimistic / Pessimistic | Optimistic | 성능 우선, 드문 충돌 (1관리자) |

---

## 배포 체크리스트

- [ ] `tests/unit/test_qa_delete_service.py` 작성 및 통과
- [ ] `tests/integration/test_admin_delete_flow.py` 작성 및 통과
- [ ] `src/ui/admin_list_tab.py` 수정 (삭제 버튼 추가)
- 현
- [ ] `src/models/qa_delete_models.py` 생성
- [ ] `src/main.py` 수정 (다이얼로그 콜백 연결)
- [ ] 모든 테스트 통과 (`pytest tests/ -v`)
- [ ] 통합 테스트: 삭제 후 → 목록 갱신 확인
- [ ] Edge case 테스트: EC-001 ~ EC-007 모두 통과
- [ ] Langfuse span 기록 확인
- [ ] 성능 검증: 삭제 < 2초, 응답 < 1초

---

## 다음 단계

✅ **Phase 2 준비 완료**: `/speckit.tasks` 실행 시 구현 작업 목록 자동 생성

**예상 타임라인**:
1. 데이터 모델 + 서비스 (1시간)
2. UI 통합 (1시간)
3. 테스트 작성 및 통과 (1시간)
4. 버그 수정 및 최적화 (30분)

**총 소요 시간**: ~3.5시간

---

**마지막 업데이트**: 2026-03-05  
**상태**: 설계 완료 ✅ → 구현 준비 완료 ✅
