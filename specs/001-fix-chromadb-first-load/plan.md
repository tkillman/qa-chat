# Implementation Plan: 목록 탭 첫 진입 데이터 정합성 수정

**Branch**: `001-fix-chromadb-first-load` | **Date**: 2026-03-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-fix-chromadb-first-load/spec.md`

## Summary

관리자 `목록 조회` 탭 진입 시(첫 진입/재진입) 항상 정본 저장소 기준 목록을 표시하도록 로딩 경로를 일관화한다. 구현은 `admin_list_tab`의 초기 렌더/탭 재진입 트리거와 `qa_list_service`의 조회 결과 처리 규약을 맞추고, 실패 시 `오류 메시지 + 빈 목록`을 즉시 반환하며 자동 재시도는 수행하지 않는 정책으로 고정한다.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Gradio 4.x, ChromaDB, Langfuse, pytest  
**Storage**: ChromaDB persistent collection (`data/chromadb`) + 초기 파일 데이터(`data/init.txt`)  
**Testing**: pytest (unit/integration/contract)  
**Target Platform**: Gradio 기반 웹 앱 (로컬/서버 실행)  
**Project Type**: 단일 Python 웹 서비스 (RAG admin + user chat)  
**Performance Goals**: 목록 탭 진입 후 첫 화면 렌더 p95 2초 이내(운영 기준 중소 데이터셋)  
**Constraints**: 탭 진입마다 정본 재조회, 실패 시 즉시 오류 상태(자동 재시도 금지), 검증되지 않은 캐시 데이터 미노출  
**Scale/Scope**: 관리자 목록 탭 로딩 경로 수정(`src/ui/admin_list_tab.py`, `src/services/qa_list_service.py`) + 관련 테스트 보강

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Gate Review

1. **관찰 가능성 우선**: PASS  
  - 기존 `admin_list_qa_items` 이벤트 로깅이 존재하며, 실패/성공 경로 모두 계측 대상로 유지한다.
2. **벡터 인식 데이터 계약**: PASS  
  - 목록 조회는 ChromaDB 정본 조회 계약(현재 시점 값 우선, 비검증 fallback 금지)을 문서화한다.
3. **사용자 중심 UI**: PASS  
  - 실패 시 명시적 오류 메시지 + 빈 목록 상태를 보여주는 UI 계약을 유지/강화한다.
4. **테스트 주도 개발**: PASS (계획상)  
  - 목록 탭 첫 진입/재진입/실패 정책을 검증하는 단위·통합 테스트를 구현 전에 정의한다.
5. **버전 관리 및 주요 변경사항**: PASS  
  - 데이터 스키마/임베딩 모델 변경이 없는 패치 성격의 버그 수정이다.

### Post-Phase 1 Gate Review

1. **관찰 가능성 우선**: PASS  
  - `research.md`, `contracts/`에 실패/성공 로깅 규약을 명시했다.
2. **벡터 인식 데이터 계약**: PASS  
  - `contracts/list-source-contract.md`에 탭 진입 시 정본 재조회 계약과 실패 처리 정책을 고정했다.
3. **사용자 중심 UI**: PASS  
  - `contracts/admin-list-ui-contract.md`에 첫 진입/재진입/오류 상태 표시 흐름을 정의했다.
4. **테스트 주도 개발**: PASS (Phase 2에서 실행)  
  - `quickstart.md`에 우선 실행 테스트 범위를 명시했다.
5. **버전 관리 및 주요 변경사항**: PASS  
  - 마이그레이션 필요 없는 PATCH 범위로 유지한다.

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-chromadb-first-load/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── README.md
│   ├── admin-list-ui-contract.md
│   ├── list-source-contract.md
│   └── list-view-response-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── main.py
├── models/
│   └── qa_list_models.py
├── services/
│   ├── chromadb_service.py
│   └── qa_list_service.py
└── ui/
   └── admin_list_tab.py

tests/
├── integration/
│   └── test_admin_list.py
└── unit/
   └── test_admin_list_tab.py
```

**Structure Decision**: 기존 단일 프로젝트 구조를 유지하고, 목록 탭 로딩 경로와 조회 서비스 경계만 수정한다. 신규 아키텍처/모듈 추가는 하지 않는다.

## Complexity Tracking

위반 없음. 헌법 원칙 내에서 기존 구조를 유지하며 해결 가능하다.

## Phase Plan

### Phase 0: Research
- 목록 탭 진입 시점 데이터 소스/실패 정책/재진입 정책 결정 근거 문서화
- ChromaDB 정본 조회 계약과 UI 노출 정책 정렬

### Phase 1: Design & Contracts
- `data-model.md`: 목록 조회 상태 모델, 에러 상태 모델, 세션 상태 전이 정의
- `contracts/`: UI 상호작용 계약, 서비스 조회 계약, 뷰 응답 계약 작성
- `quickstart.md`: 버그 재현/수정 검증/테스트 실행 절차 정리

### Phase 2: Task Planning (next command)
- `/speckit.tasks`에서 구현 작업을 테스트 우선 순서로 분해
