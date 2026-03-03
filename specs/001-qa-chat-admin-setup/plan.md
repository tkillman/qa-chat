# 구현 계획: QA Chat 관리자 및 초기 설정

**브랜치**: `001-qa-chat-admin-setup` | **작성일**: 2026-03-03 | **명세서**: [spec.md](spec.md)

**입력**: 기능 명세서로부터: 관리자 로그인, ChromaDB 업데이트, 초기 로딩, 질문 답변 기능

## 요약

QA Chat 애플리케이션의 핵심 RAG (Retrieval-Augmented Generation) 기능을 구현합니다. Gradio 기반 사용자/관리자 UI에서:
- 앱 시작 시 init.txt ≫ ChromaDB 로드
- 관리자 로그인(패스워드 1234) 및 Q&A 관리
- 사용자 질문 시 ChromaDB 검색 및 답변 제공
- Langfuse 기반 전체 추적

## 기술 컨텍스트

**언어**: Python 3.11+  
**주요 의존성**: Gradio, ChromaDB, Langfuse, LangChain  
**저장소**: init.txt (텍스트 파일 기반 영구 저장소)  
**백터 DB**: ChromaDB (in-memory 또는 persistent)  
**테스팅**: pytest, Gradio test suite  
**대상 플랫폼**: 웹 애플리케이션 (Gradio 배포)  
**프로젝트 타입**: RAG 기반 Q&A 챗봇  
**성능 목표**: 검색 응답 <1초, init.txt 로드 <5초  
**제약사항**: 메모리 효율성 (ChromaDB 작은 인스턴스), 패스워드 보안 (본격적 제품에서는 해싱 필요)  
**범위**: 초기 MVP - 단순 텍스트 기반 Q&A, 관리자 CRUD

## 헌법 확인

✅ **관찰 가능성 우선**: Langfuse로 ChromaDB 검색/업데이트/로그인 이벤트 추적  
✅ **벡터 인식 계약**: 임베딩 모델, 유사도 임계값, 검색 상위 결과 명시  
✅ **사용자 중심 UI**: Gradio 컴포넌트 (입력 검증, 상태 관리, 실시간 피드백)  
✅ **테스트 주도 개발**: 단위/통합/계약 테스트 작성 후 구현  
✅ **버전 관리**: Semantic versioning (v1.0.0 초기)

## 프로젝트 구조

### 문서 (이 기능)

```text
specs/001-qa-chat-admin-setup/
├── plan.md              # 이 파일
├── spec.md              # 명세서
├── research.md          # (TODO) 임베딩 모델/라이브러리 결정
├── data-model.md        # (TODO) 데이터베이스 스키마
├── quickstart.md        # (TODO) 로컬 개발 시작
└── contracts/           # (TODO) API 컨트랙트
```

### 소스 코드 (저장소 루트)

```text
src/
├── config.py                    # 설정 (패스워드, 임계값, 모델)
├── main.py                      # Gradio 앱 진입점
├── models/
│   └── qa_item.py              # QA 아이템 데이터 클래스
├── services/
│   ├── chromadb_service.py      # ChromaDB 유틸리티 (초기화, 검색, 업데이트)
│   ├── embedding_service.py     # 임베딩 생성 서비스
│   ├── langfuse_service.py      # Langfuse 추적
│   └── file_service.py          # init.txt 읽기/쓰기
└── ui/
    ├── admin_ui.py              # 관리자 화면 (로그인, Q&A 관리)
    └── user_ui.py               # 사용자 화면 (질문 입력, 답변 표시)

tests/
├── unit/
│   ├── test_chromadb_service.py
│   ├── test_embedding_service.py
│   └── test_file_service.py
├── integration/
│   ├── test_admin_workflow.py    # 로그인 → Q&A 입력 → DB 업데이트
│   └── test_user_workflow.py     # 질문 → 검색 → 답변
└── contract/
    ├── test_chromadb_contract.py # ChromaDB 동작 검증
    └── test_gradio_ui_contract.py # Gradio 컴포넌트 계약
```

**구조 선택**: 단일 프로젝트 (Option 1) - Gradio 앱이 모든 로직을 포함합니다.

## 복잡성 추적

> 현재 헌법 위반 없음. 모든 원칙이 충족되는 범위 내에서 설계됨.

| 부분 | 상태 | 메모 |
|------|-----|------|
| 테스트 커버리지 | ✅ | TDD 적용 (테스트 먼저) |
| 관찰성 | ✅ | Langfuse 통합 |
| 데이터 계약 | ✅ | 벡터 임계값 명시 |
| UI/UX | ✅ | Gradio 기반 |
| 설정 | ✅ | config.py에 중앙화 |
