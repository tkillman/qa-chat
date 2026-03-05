# 변경 이력 (CHANGELOG)

모든 주요 변경사항을 이 파일에 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/)를 참고합니다.

---

## [1.1.0] - 2026-03-05 (관리자 Q&A 삭제 기능)

### 추가됨

#### 핵심 기능 (4개 사용자 스토리)

- **US1 삭제 버튼 - 관리자 목록 조회 탭**
  - 각 Q&A 항목 옆 🗑️ 삭제 버튼 추가
  - 버튼 위치: 테이블 우측 액션 컬럼
  - 삭제 권한: 관리자 로그인 필수
  - HTML 이스케이핑: XSS 방지
  
- **US2 삭제 확인 다이얼로그**
  - 실수 삭제 방지 2단계 확인
  - 모달 레이아웃: 질문/답변 미리보기 + 확인/취소 버튼
  - 응답성: < 1초 표시
  - 스타일링: Gradio 4.x 네이티브 컴포넌트
  
- **US3 삭제 실행 및 Langfuse 추적**
  - ChromaDB에서 영구 삭제 (`delete_by_id`)
  - 삭제 속도: < 2초 (중소 규모 데이터셋)
  - 관찰 가능성: Langfuse trace 기록 (qa_id, admin_user, latency_ms)
  - 오류 처리: 6가지 분류 (not_found, db_connection_error, network_error, timeout, db_operation_error, unknown_error)
  
- **US4 삭제 상태 메시지**
  - 진행: "삭제 중..." (toast)
  - 성공: "✓ 삭제되었습니다" (목록 자동 갱신)
  - 실패: "❌ 삭제 실패했습니다 - [원인]"
  - 페이지 자동 조정: 마지막 항목 삭제 시 Page 1 리셋

#### 기술 기반

- **서비스 계층**
  - `QADeleteService`: 삭제 로직 + Langfuse 추적
  - `QAListService`: 관리자 목록 조회 (페이지네이션 10개 고정)
  
- **데이터 모델**
  - `QADeleteRequest`: 삭제 요청 (qa_id, admin_user, timestamp)
  - `QADeleteResult`: 삭제 응답 (success, message, error_reason)
  - `QAListRequest`/`QAListResponse`: 목록 조회 계약
  
- **UI 컴포넌트**
  - `admin_list_tab.py`: 관리자 목록 조회 UI + 삭제 버튼/다이얼로그
  - 상태 관리: Gradio State (`deletion_state`, `current_page`)
  - 보안: HTML escape (`html.escape`, `json.dumps`)

#### 테스트 (156개 추가, 총 250개)

- **계약 테스트 (15개)**
  - `test_chromadb_delete.py`: ChromaDB 삭제 API 계약 (15개)
    - 기본 동작: 삭제 성공, 반환값 검증
    - 오류 처리: not_found, empty_string, None, permission_error, timeout
    - 동시성: idempotent (멱등성), permanent (영구성)
  
- **통합 테스트 (9개)**
  - `test_admin_delete_flow.py`: 전체 삭제 플로우 (9개)
    - end-to-end: 버튼 → 다이얼로그 → 삭제 → 갱신
    - 페이지 리셋: 마지막 항목 삭제 시 Page 1 이동
    - 상태 메시지: 진행/성공/실패 toast
    - 동시 삭제: first-wins Optimistic 처리
  
- **단위 테스트 (132개)**
  - `test_qa_delete_service.py`: 삭제 서비스 로직 (50개)
  - `test_qa_list_service.py`: 목록 조회 서비스 (42개)
  - `test_admin_list_tab.py`: UI 컴포넌트 (40개)

#### 문서

- **specs/002-delete-qa-item/**
  - `spec.md`: 요구사항 명세 (9개 시나리오)
  - `plan.md`: 기술 계획 (헌법 검수, 프로젝트 구조)
  - `research.md`: 기술 결정 (삭제 전략, UI, 보안)
  - `data-model.md`: 엔티티 정의 (QADeleteRequest, QADeleteResult)
  - `tasks.md`: 구현 작업 분해 (46개 작업, 7단계)
  - `quickstart.md`: 수동 검증 시나리오 (4가지 + 엣지 케이스)
  - `contracts/`: UI/서비스 계약 (4개 파일)

### 변경됨

- `admin_list_tab.py`: 목록 조회 UI 재구성 (테이블 → HTML + 버튼)
- `main.py`: 관리자 탭에 `admin_list_tab` 통합
- `conftest.py`: 삭제 관련 fixture 추가 (`qa_delete_service`)

### 보안 강화

- XSS 방지: `json.dumps` + `html.escape` 이중 이스케이핑
- CSRF 방지: 관리자 인증 플래그 (`admin_logged_in`) 체크
- 권한 검증: 모든 삭제 작업에서 로그인 상태 확인

### 성능

- 삭제 완료: < 2초 (중소 규모 데이터셋)
- 목록 갱신: < 1초 (페이지당 10개)
- 테스트 실행: 250개 14.71초 ✅

### 엣지 케이스 검증 (7개)

- EC-001: 페이지 새로고침 중 삭제 (Gradio SPA 제약사항)
- EC-002: 동시 삭제 → "항목을 찾을 수 없습니다" 오류
- EC-003: 네트워크 오류 → "네트워크 오류가 발생했습니다" 메시지
- EC-004: ChromaDB 응답 없음 → 타임아웃 처리
- EC-005: 항목 1개만 → 삭제 후 빈 상태 표시
- EC-006: 페이지 2 마지막 항목 → Page 1 리셋
- EC-007: 버튼 중복 클릭 → Gradio 이벤트 큐 자동 방지

### 고려사항 (Known Issues)

- 삭제 실행 취소 (Undo) 기능 없음 (향후 계획)
- 대량 일괄 삭제 미지원 (1개씩만 삭제)

### 의존성

```
Python>=3.12
gradio>=4.26.0
chromadb>=0.4.24
langfuse>=2.12.0
pytest>=9.0.0
python-dotenv>=1.0.0
langchain>=0.0.300
```

---

## [1.0.0] - 2026-03-03 (MVP 릴리스)

### 추가됨

#### 코어 기능 (4개 사용자 스토리)

- **US1 초기 데이터 로드 (Phase 1-3)**
  - 앱 시작 시 `init.txt`의 Q&A 데이터를 ChromaDB로 로드
  - 지원 형식: 줄 단위 JSON
  - 성능: 1000개 항목 로드 ~100ms
  
- **US2 관리자 로그인 (Phase 4)**
  - 패스워드 인증 (기본값: `1234`)
  - 환경변수 `ADMIN_PASSWORD` 사용
  - 보안: 정확한 패스워드 일치 검증
  
- **US3 Q&A 관리 - 추가/수정 (Phase 5)**
  - 관리자가 질문과 답변 추가
  - 중복 질문 자동 덮어쓰기
  - 입력 제한: 질문 500자, 답변 2000자
  - ChromaDB 실시간 업데이트
  
- **US4 질문 답변 - 검색 (Phase 6)**
  - 사용자 질문 입력 받기
  - 벡터 유사도 기반 검색
  - 유사도 임계값 0.7 이상만 반환
  - 최대 1개 결과 반환

#### 기술 기반

- **서비스 계층**
  - `FileService`: 파일 I/O (JSON 직렬화)
  - `ChromaDBService`: 벡터 저장소 관리
  - `EmbeddingService`: LangChain 기반 임베딩
  - `AuthService`: 패스워드 검증
  - `QAUpdateService`: Q&A 관리
  - `UserSearchService`: 질문 검색
  - `InitLoader`: 초기 데이터 로드
  - `LangfuseService`: 관찰성/추적 로깅
  
- **데이터 모델**
  - `QAItem`: Q&A 항목 데이터 클래스
  - JSON 직렬화/역직렬화
  - 해시 키 기반 중복 검사
  
- **UI**
  - Gradio 4.26.0+ 기반 웹 인터페이스
  - 사용자 탭: 질문 입력 & 답변 표시
  - 관리자 탭: 로그인 & Q&A 관리

#### 테스트 (94개)

- **단위 테스트 (48개)**
  - `test_auth.py`: 인증 검증 (12개)
  - `test_qa_update.py`: Q&A 관리 (13개)
  - `test_user_search.py`: 질문 검색 (12개)
  - `test_file_service.py`: 파일 I/O (11개)

- **통합 테스트 (30개)**
  - `test_admin_login.py`: 관리자 로그인 (12개)
  - `test_qa_update.py`: Q&A 관리 (11개)
  - `test_initial_load.py`: 초기 로드 (7개)

- **계약 테스트 (16개)**
  - `test_chromadb_contract.py`: 벡터 저장소 (9개)
  - 임베딩 차원, 유사도 범위 검증

#### 구성 파일

- `.env` 템플릿: 환경 변수 기본 설정
- `pytest.ini`: pytest 설정
- `.gitignore`: git 무시 파일 목록
- `requirements.txt`: 의존성 명세

#### 문서

- `README.md`: 프로젝트 개요 및 사용 가이드
- `CONTRIBUTING.md`: 개발자 기여 가이드
- `CHANGELOG.md`: 이 파일

### 변경됨

- ChromaDB 설정: 기존 `Settings` → 새로운 `PersistentClient` (최신 방식)
- 테스트 격리: 테스트 전후로 임시 데이터 정리

### 고건사항 (Known Issues)

- 없음 (MVP 완성)

### 의존성

```
Python>=3.12
gradio>=4.26.0
chromadb>=0.4.24
langfuse>=2.12.0
pytest>=7.4.3
python-dotenv>=1.0.0
langchain>=0.0.300
```

---

## 향후 계획 (Roadmap)

### Phase 7: 최적화 및 배포 준비

- [ ] 성능 최적화
  - [ ] 임베딩 캐싱
  - [ ] 배치 검색 처리
  - [ ] 메모리 효율화
  
- [ ] 에러 처리 개선
  - [ ] Graceful degradation
  - [ ] 재시도 로직
  - [ ] 상세 에러 메시지
  
- [ ] 문서 개선
  - [ ] API 문서 (Swagger/OpenAPI)
  - [ ] 개발 가이드 확장
  - [ ] 문제 해결 가이드 (Troubleshooting)

### Phase 8: 확장 기능

- [ ] 다중 사용자 지원
  - [ ] 사용자 인증
  - [ ] 역할 기반 접근 제어 (RBAC)
  
- [ ] 데이터베이스 마이그레이션
  - [ ] SQLite 지원
  - [ ] PostgreSQL 지원
  
- [ ] 관리자 기능 확장
  - [ ] Q&A 통계 대시보드
  - [ ] 검색 기록 분석
  - [ ] 데이터 내보내기/가져오기

- [ ] 배포 및 CI/CD
  - [ ] Docker 컨테이너화
  - [ ] GitHub Actions CI/CD
  - [ ] Heroku/Railway 배포 샘플

---

## 버전 관리 정책

### Semantic Versioning (SemVer)

`MAJOR.MINOR.PATCH`

- **MAJOR**: 호환되지 않는 변경
- **MINOR**: 하위 호환 기능 추가
- **PATCH**: 하위 호환 버그 수정

예: `1.2.3` → 주(1) 버전, 부(2) 버전, 패치(3) 버전

### 릴리스 주기

- **안정 버전**: 분기마다 (이전 버전 지원 2단계)
- **개발 버전**: 지속적 통합 (매일 분석)

---

## 기술 부채 (Technical Debt)

현재 MVP에서는 다음 사항들이 미완성 상태입니다:

- [ ] 유연한 인증 시스템 (현재: 고정 패스워드)
- [ ] 관리자 기능 UI 확장 (기본 폼만 구현)
- [ ] 사용자 피드백 시스템
- [ ] 고급 검색 필터 (현재: 단순 텍스트 유사도)
- [ ] 성능 모니터링 대시보드

---

## 공헌자 (Contributors)

### v1.0.0

- **Project Lead**: [Your Name]
- **Developers**: [Team Members]
- **QA**: [QA Team]

기여해주신 모든 분들께 감사합니다!

---

## 미래 버전 (Unreleased)

### 예정 기능

- [ ] 멀티 턴 대화 (대화 컨텍스트 유지)
- [ ] 자동 Q&A 생성 (NLP 기반)
- [ ] 사용자 피드백 기반 개선
- [ ] 다국어 지원

---

마지막 업데이트: 2026-03-03
