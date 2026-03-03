---
description: "QA Chat 관리자 및 초기 설정 구현 작업 목록"
---

# 작업: QA Chat 관리자 및 초기 설정

**입력**: 설계 문서 from `/specs/001-qa-chat-admin-setup/`  
**필수 조건**: plan.md (필수), spec.md (필수)

**테스트**: 각 사용자 스토리별로 필수. 테스트 우선 작성 (TDD).

**구성**: 사용자 스토리별로 작업이 그룹화되어 독립적 구현 및 테스트를 가능하게 합니다.

## 형식: `[ID] [P?] [Story?] Description`

- **[P]**: 병렬 실행 가능 (서로 다른 파일, 의존성 없음)
- **[Story]**: 사용자 스토리 (예: US1, US2, US3)
- 정확한 파일 경로 포함

## 경로 규칙

- **단일 프로젝트**: `src/`, `tests/` (저장소 루트)
- 웹 앱, 모바일 등 조정 불필요

---

## Phase 1: Setup (공유 인프라)

**목적**: 프로젝트 초기화 및 기본 구조

- [x] T001 프로젝트 구조 생성 (src/, tests/, specs/ 디렉토리)
- [x] T002 [P] Python 3.11+ 및 의존성 설치 (Gradio, ChromaDB, Langfuse, LangChain)
- [x] T003 [P] pytest 및 테스트 설정 구성
- [x] T004 [P] .gitignore 업데이트 (ChromaDB 캐시, __pycache__, .env)
- [x] T005 src/config.py에 설정 (패스워드=1234, 유사도_임계값=0.7) 정의

---

## Phase 2: Foundational (차단 조건)

**목적**: 모든 사용자 스토리가 의존하는 핵심 인프라

**⚠️ 중요**: 이 단계가 완료되어야 사용자 스토리 작업 시작 가능

- [x] T006 src/models/qa_item.py 생성 (질문, 답변, 임베딩, 메타데이터 데이터 클래스)
- [x] T007 [P] src/services/file_service.py - init.txt 읽기/쓰기 유틸리티 구현
- [x] T008 [P] src/services/embedding_service.py - 임베딩 생성 서비스 (LangChain 경유)
- [x] T009 [P] src/services/chromadb_service.py - ChromaDB 유틸리티 (초기화, 검색, 업데이트, 삭제)
- [x] T010 src/services/langfuse_service.py - Langfuse 추적 래퍼 구현
- [x] T011 [P] tests/unit/test_file_service.py 작성 (init.txt 읽기/쓰기 테스트)
- [x] T012 [P] tests/contract/test_chromadb_contract.py - ChromaDB 계약 테스트 (검색, 임베딩 임계값)

**체크포인트**: Foundational 완료 - 모든 사용자 스토리 작업 시작 가능

---

## Phase 3: User Story 1 - 초기 로딩 (우선순위: P1) 🎯

**목표**: 앱 실행 시 init.txt의 데이터를 ChromaDB에 로드

**독립적 테스트**: init.txt가 존재할 때/없을 때 app 시작 시 ChromaDB가 올바르게 초기화되는지 확인 가능

### US1 테스트

> **참고: 구현 전에 다음 테스트 작성 및 실패 확인**

- [x] T013 [P] [US1] tests/integration/test_initial_load.py - init.txt 없음 → 빈 데이터 테스트
- [x] T014 [P] [US1] tests/integration/test_initial_load.py - init.txt 있음 → 데이터 로드 테스트
- [x] T015 [US1] tests/integration/test_initial_load.py - init.txt 형식 오류 → 기본값 처리 테스트

### US1 구현

- [x] T016 src/main.py에 초기화 함수 생성 (on_startup hook)
- [x] T017 [US1] src/services/init_loader.py - init.txt에서 ChromaDB로 로드하는 로직 구현
- [x] T018 [US1] src/main.py의 on_startup에서 T017 호출하도록 연결
- [x] T019 [US1] Langfuse로 초기 로드 이벤트 추적 (로드된 항목 수, 소요 시간)
- [x] T020 [US1] 에러 처리: init.txt 손상 시 로그 및 빈 상태로 시작

**체크포인트**: US1 완료 - app 시작 시 ChromaDB 초기화 작동

---

## Phase 4: User Story 2 - 관리자 로그인 (우선순위: P1)

**목표**: 패스워드(1234) 검증 후 관리자 화면 진입

**독립적 테스트**: Gradio 로그인 UI에서 패스워드 입력/검증/화면 전환을 독립적으로 테스트 가능

### US2 테스트

> **참고: 구현 전에 다음 테스트 작성 및 실패 확인**

- [x] T021 [P] [US2] tests/unit/test_auth.py - 올바른 패스워드 검증 테스트 (12개 테스트)
- [x] T022 [P] [US2] tests/unit/test_auth.py - 틀린 패스워드 검증 테스트
- [x] T023 [US2] tests/integration/test_admin_login.py - Gradio 로그인 화면 상태 관리 테스트 (12개 테스트)

### US2 구현

- [x] T024 [P] [US2] src/services/auth_service.py - 패스워드 검증 로직
- [x] T025 [US2] src/main.py - Gradio 로그인 UI 컴포넌트 구현
- [x] T026 [US2] src/main.py - 상태 관리 (admin_logged_in)
- [x] T027 [US2] src/main.py - 로그인 UI 통합 및 라우팅
- [x] T028 [US2] Langfuse로 로그인 시도 추적 (성공/실패)

**체크포인트**: US2 완료 - 관리자 로그인 작동, 인증 후 화면 전환

---

## Phase 5: User Story 3 - ChromaDB 업데이트 (우선순위: P2)


**목표**: 관리자가 질문/답변 입력 후 ChromaDB 및 init.txt 업데이트

**독립적 테스트**: 관리자 화면에서 질문/답변 입력 → DB 업데이트 → init.txt 저장 확인 가능

### US3 테스트

> **참고: 구현 전에 다음 테스트 작성 및 실패 확인**

- [ ] T029 [P] [US3] tests/unit/test_chromadb_update.py - 단일 Q&A 추가 테스트
- [ ] T030 [P] [US3] tests/unit/test_chromadb_update.py - 중복 질문 처리 테스트
- [ ] T031 [US3] tests/integration/test_admin_qa_workflow.py - 관리자 UI에서 Q&A 입력 → 저장 전체 흐름
- [ ] T032 [US3] tests/integration/test_admin_qa_workflow.py - app 재시작 시 저장된 데이터 로드 확인

### US3 구현

- [ ] T033 [P] [US3] src/services/qa_service.py - Q&A 항목 추가/수정/삭제 로직
- [ ] T034 src/ui/admin_qa_ui.py - 관리자 Q&A 입력 화면 (Gradio 텍스트 박스, 버튼)
- [ ] T035 [US3] src/ui/admin_qa_ui.py - "DB 업데이트" 버튼 → T033, T007 (service, file_service) 호출
- [ ] T036 [US3] src/services/qa_service.py에서 ChromaDB 업데이트 (임베딩 생성 → 저장)
- [ ] T037 [US3] src/services/file_service.py와 연동하여 init.txt 저장
- [ ] T038 [US3] Langfuse로 각 Q&A 업데이트 추적 (추가/수정/삭제, 임베딩 생성 시간)
- [ ] T039 [US3] UI 피드백: 업데이트 성공/실패 메시지 표시

**체크포인트**: US3 완료 - 관리자가 Q&A 추가/수정 가능, init.txt + ChromaDB 동기화

---

## Phase 6: User Story 4 - 질문 답변 기능 (우선순위: P2)

**목표**: 사용자 질문 입력 시 ChromaDB에서 검색하여 답변 제공

**독립적 테스트**: 사용자 UI에서 질문 입력 → 검색 → 답변 표시 확인 가능

### US4 테스트

> **참고: 구현 전에 다음 테스트 작성 및 실패 확인**

- [ ] T040 [P] [US4] tests/unit/test_qa_search.py - 정확 일치 검색 테스트
- [ ] T041 [P] [US4] tests/unit/test_qa_search.py - 유사 검색 (유사도 임계값 0.7 이상) 테스트
- [ ] T042 [P] [US4] tests/unit/test_qa_search.py - 검색 결과 없음 테스트
- [ ] T043 [US4] tests/integration/test_user_qa_workflow.py - 사용자 UI 질문 입력 → 답변 표시 전체 흐름

### US4 구현

- [ ] T044 [P] [US4] src/services/qa_search_service.py - ChromaDB 검색 로직 (유사도 임계값 적용)
- [ ] T045 src/ui/user_qa_ui.py - 사용자 질문 입력 화면 (Gradio 텍스트박스, 제출 버튼)
- [ ] T046 [US4] src/ui/user_qa_ui.py - 질문 제출 → T044 검색 호출
- [ ] T047 [US4] src/ui/user_qa_ui.py - 답변 표시 (검색 결과 있음 / 없음)
- [ ] T048 [US4] Langfuse로 모든 사용자 질문 추적 (질문, 검색 결과, 구조, 응답 시간)
- [ ] T049 [US4] 에러 처리: 검색 실패, 임베딩 오류 시 사용자 친화적 메시지

**체크포인트**: US4 완료 - 사용자가 질문 입력 후 답변 수신 가능

---

## Phase 7: Polish & 교차 기능

**목적**: 다중 스토리에 영향을 주는 개선사항

- [ ] T050 [P] docs/README.md - 로컬 개발 환경 설정, 실행 방법 작성
- [ ] T051 [P] specs/001-qa-chat-admin-setup/quickstart.md - 빠른 시작 가이드
- [ ] T052 specs/001-qa-chat-admin-setup/data-model.md - 최종 데이터 모델 문서화
- [ ] T053 [P] tests/unit/ 및 tests/integration/ 추가 엣지 케이스 테스트
- [ ] T054 Performance 최적화: ChromaDB 쿼리 속도, 임베딩 캐싱
- [ ] T055 예외 처리 강화: 네트워크 오류, ChromaDB 손상, 임베딩 모델 로드 실패
- [ ] T056 [P] 전체 통합 테스트 (app 시작 → 로그인 → Q&A 입력 → 사용자 질문 전체 흐름)
- [ ] T057 보안: 패스워드 해싱 (선택, MVP 이후), 관리자 세션 암호화
- [ ] T058 UI/UX: 로딩 상태 표시, 진행 표시기, 사용자 친화적 오류 메시지

---

## 의존성 및 실행 순서

### Phase 의존성

- **Setup (Phase 1)**: 의존성 없음 - 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 필요 - 모든 사용자 스토리 차단
- **User Stories (Phase 3~6)**: Foundational 완료 후 시작 가능
  - US1, US2 동시 진행 가능 (P1, 상호 독립적)
  - US3, US4 동시 진행 가능 (P2, US1~2 이후)
- **Polish (Phase 7)**: 모든 사용자 스토리 완료 후

### 사용자 스토리 의존성

- **US1 (P1)**: Foundational 완료 후 - 다른 스토리와 독립적
- **US2 (P1)**: Foundational 완료 후 - 다른 스토리와 독립적
- **US3 (P2)**: Foundational + US1, US2 완료 후 - US4와 독립적
- **US4 (P2)**: Foundational + US1 완료 후 - US3와 독립적이나 US1이 필요

### 각 스토리 내부

- 테스트 작성 및 실패 확인
- 모델 → 서비스 → UI 순서
- 각 UI 변경 후 Langfuse 추적 통합

### 병렬 기회

- **Setup (Phase 1)**: [P] 표시 작업들 병렬 실행 가능
- **Foundational (Phase 2)**: [P] 표시 작업들 병렬 실행 가능
- **Foundational 완료 후**: US1, US2 동시 진행 (다른 팀원)
- **US1, US2 완료 후**: US3, US4 동시 진행
- 각 스토리 내 [P] 작업들 병렬 실행

---

## 병렬 예시: US1 (초기 로딩)

팀원 A, B가 있을 경우:

1. **병렬 실행 (Foundational 완료 후)**:
   - A: T013 테스트 작성 → T016, T017, T018 구현
   - B: T014, T015 추가 테스트 작성
   
2. **순차 (테스트 완료 후)**:
   - A: T019, T020 Langfuse 통합 및 에러 처리
   
3. **검증**: 전체 통합 테스트

---

## 병렬 예시: US2 + US3 병렬

팀원 A, B 독립적 진행 (Foundational 완료 후):

**팀원 A (US2 로그인)**:
T021, T022, T023, T024, T025, T026, T027, T028

**팀원 B (US1 초기 로딩)**:
T013~T020

→ US1, US2 완료 후 → US3 (Q&A 업데이트) 시작

---

## MVP 범위

**초기 MVP (US1 + US2만)**:
- ✅ 앱 시작 시 init.txt 로드
- ✅ 관리자 로그인 (패스워드 1234)
- ❌ ChromaDB 업데이트 (나중에)
- ❌ 사용자 질문 (나중에)

**Full Product (모든 US)**:
- ✅ 초기 로딩 + 로그인 + 업데이트 + 질문 답변

---

**구현 전략**: MVP 먼저 (US1, US2) → 검증 → 사용자 기능 추가 (US3, US4)
