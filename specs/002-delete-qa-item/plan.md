# Implementation Plan: Q&A 항목 삭제 기능

**Branch**: `002-delete-qa-item` | **Date**: 2026-03-05 | **Spec**: `specs/002-delete-qa-item/spec.md`
**Input**: Feature specification from `specs/002-delete-qa-item/spec.md`

## Summary

관리자 목록 조회 탭에서 각 Q&A 카드에 삭제 버튼을 노출하고, 확인 다이얼로그를 거쳐 ChromaDB에서 항목을 삭제한 뒤 목록을 즉시 갱신한다. 기술적으로는 `admin_list_tab`의 상태 관리(`gr.State`)와 이벤트 체인을 확장하고, `QADeleteService`를 통해 삭제·오류처리·Langfuse 기록을 일관 처리한다.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Gradio 4.x, ChromaDB 0.5+, pytest, Langfuse SDK(옵션)  
**Storage**: ChromaDB 로컬 persistent storage + `data/init.txt` (JSONL)  
**Testing**: pytest (unit/integration/contract/performance)  
**Target Platform**: Windows/Linux 로컬 실행 환경 (Gradio 서버)  
**Project Type**: 단일 Python 애플리케이션 (Gradio UI + 서비스 레이어)  
**Performance Goals**: 삭제 완료 < 2초, 다이얼로그 응답 < 1초  
**Constraints**: 관리자 인증 상태에서만 삭제 허용, optimistic concurrency(선삭제 우선), UI는 Gradio 컴포넌트 사용  
**Scale/Scope**: 관리 대상 Q&A 수 ~100개 기준, 페이지당 10개 표시

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [PASS] **I. 관찰 가능성 우선**: 삭제 성공/실패 이벤트를 `LangfuseService`로 기록 (`qa_id`, `admin_user`, `success`, `error_message` 포함).
- [PASS] **II. 벡터 인식 데이터 계약**: 삭제 식별자는 질문 해시 ID(`QAItem.get_hash_key`)를 사용하며, ChromaDB 삭제 계약(미존재 시 오류)을 계약 테스트로 명시.
- [PASS] **III. 사용자 중심 UI**: 버튼 노출, 확인 다이얼로그, 취소 경로, 진행/결과 토스트를 Gradio 상에서 일관 상태로 관리.
- [PASS] **IV. 테스트 주도 개발**: unit/integration/contract 테스트를 기능 단위로 우선 작성·보강.
- [PASS] **V. 버전 관리 및 주요 변경사항**: 기존 API 파손 없는 기능 추가(MINOR 성격), 마이그레이션 불필요.

## Project Structure

### Documentation (this feature)

```text
specs/002-delete-qa-item/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── main.py
├── models/
│   ├── qa_item.py
│   ├── qa_list_models.py
│   └── qa_delete_models.py
├── services/
│   ├── chromadb_service.py
│   ├── langfuse_service.py
│   ├── qa_list_service.py
│   └── qa_delete_service.py
└── ui/
    └── admin_list_tab.py

tests/
├── unit/
│   ├── test_admin_list_tab.py
│   └── test_qa_delete_service.py
├── integration/
│   └── test_admin_delete_flow.py
├── contract/
│   └── test_chromadb_delete.py
└── performance/
```

**Structure Decision**: 단일 프로젝트 구조를 유지하며, UI(`src/ui`) - 서비스(`src/services`) - 모델(`src/models`) 레이어를 확장하는 방식으로 구현한다.

## Phase 0: Research Plan

### Unknowns / Research Tasks

본 기능 스펙의 핵심 미확정 사항은 Clarification 세션에서 해소되었으며, 추가 `NEEDS CLARIFICATION` 항목은 없음.

추가 검증 대상:
1. Gradio에서 카드 단위 삭제 액션 바인딩 패턴
2. ChromaDB 삭제 실패(미존재/연결오류) 사용자 메시지 표준
3. Langfuse 이벤트 필드 최소 집합

산출물: `research.md`

## Phase 1: Design & Contracts Plan

1. 데이터 모델 명세 정리 (`data-model.md`)
2. UI/서비스 계약 문서화 (`contracts/admin-delete-ui-contract.md`, `contracts/qa-delete-service-contract.md`)
3. 로컬 실행·검증 절차 작성 (`quickstart.md`)
4. 에이전트 컨텍스트 갱신 (`.specify/scripts/bash/update-agent-context.sh copilot`)

## Post-Design Constitution Check

- [PASS] 관찰성: 삭제 이벤트 표준 필드 계약 문서화 완료 예정
- [PASS] 벡터 계약: 삭제 식별자/오류 semantics 계약 테스트에 반영 예정
- [PASS] 사용자 중심 UI: 취소/확인/진행/결과 상태 흐름을 계약으로 명시
- [PASS] TDD: 테스트 우선 작성 흐름 유지
- [PASS] 버전 정책: 기존 기능 파손 없이 확장

## Complexity Tracking

위반 항목 없음.
