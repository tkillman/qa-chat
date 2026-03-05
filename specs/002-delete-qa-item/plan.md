# Implementation Plan: Q&A 항목 삭제 기능

**Branch**: `002-delete-qa-item` | **Date**: 2026-03-05 | **Spec**: `specs/002-delete-qa-item/spec.md`
**Input**: Feature specification from `/specs/002-delete-qa-item/spec.md`

## Summary

관리자 목록 조회의 테이블 행마다 삭제 버튼을 제공하고, 확인 다이얼로그(`예/아니오`)를 통해 ChromaDB 삭제를 실행한다. 삭제 진행/성공/실패는 Gradio toast로 안내하며, 마지막 항목 삭제 시 페이지를 1로 리셋하고 목록을 재조회한다. 삭제 이벤트는 Langfuse span으로 추적한다.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: Gradio, ChromaDB, Langfuse, pytest  
**Storage**: ChromaDB(벡터/메타데이터), 로컬 파일(data/init.txt)  
**Testing**: pytest (unit/integration/contract)  
**Target Platform**: Windows/macOS/Linux에서 실행되는 Gradio 웹 앱  
**Project Type**: 단일 Python 웹 애플리케이션  
**Performance Goals**: 삭제 요청 후 2초 이내 처리(SC-003), 다이얼로그 1초 이내 표시(SC-002)  
**Constraints**: 확인 다이얼로그 유지, 페이지당 10개 고정, 관리자 인증 전제, Langfuse 미가용 시에도 삭제 자체는 진행  
**Scale/Scope**: 관리자 목록(약 100개 규모)에서 단건 삭제 중심

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Gate

1. **관찰 가능성 우선 (원칙 I)**: 삭제 요청/결과를 Langfuse span으로 기록한다. **PASS**  
2. **벡터 인식 데이터 계약 (원칙 II)**: 삭제 입력(`qa_id`)과 결과(`success/error_reason`) 계약을 문서화한다. **PASS**  
3. **사용자 중심 UI (원칙 III)**: 확인 다이얼로그, 명확한 오류/상태 메시지, 중복 클릭 방지 포함. **PASS**  
4. **테스트 주도 개발 (원칙 IV)**: 단위/통합/계약 테스트로 삭제 플로우 검증. **PASS**  
5. **버전/변경 관리 (원칙 V)**: 기존 모델/스키마 파괴 변경 없음, 마이그레이션 불필요. **PASS**

### Post-Phase 1 Re-check

Phase 1 산출물(`research.md`, `data-model.md`, `contracts/`, `quickstart.md`) 기준으로 재검토 완료:

- Langfuse 계측 지점 및 필드 정의됨 → **PASS**
- 삭제 요청/응답 계약 및 UI 플로우 계약 문서화됨 → **PASS**
- 테이블 UI + 확인 다이얼로그 + toast 정책 명시됨 → **PASS**
- 테스트 실행 절차(quickstart) 및 대상 테스트 스위트 명시됨 → **PASS**
- 주요/파괴적 계약 변경 없음 → **PASS**

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
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── models/
│   └── qa_delete_models.py
├── services/
│   └── qa_delete_service.py
└── ui/
  └── admin_list_tab.py

tests/
├── contract/
├── integration/
│   └── test_admin_delete_flow.py
└── unit/
  ├── test_admin_list_tab.py
  └── test_qa_delete_service.py
```

**Structure Decision**: 단일 프로젝트 구조를 유지한다. UI(`src/ui`), 서비스(`src/services`), 모델(`src/models`)에 변경을 국소화하고 기존 `tests/` 계층에서 검증한다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
