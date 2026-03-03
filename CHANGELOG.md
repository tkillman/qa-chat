# 변경 이력 (CHANGELOG)

모든 주요 변경사항을 이 파일에 기록합니다.

형식은 [Keep a Changelog](https://keepachangelog.com/)를 참고합니다.

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
