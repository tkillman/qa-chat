# Contracts: 관리자 질문답변 목록 조회

**Feature**: 001-admin-qa-list  
**Date**: 2026-03-05

## 계약 부재 이유

이 기능은 **읽기 전용** 목록 조회 기능으로, 외부 시스템이나 다른 서비스에 노출되는 새로운 인터페이스나 계약을 생성하지 않습니다.

## 기존 계약 활용

대신, 다음 기존 계약들을 활용합니다:

### 1. ChromaDB 계약 (기존)

**위치**: `tests/contract/test_chromadb_contract.py`

**내용**:
- ChromaDB collection의 `get()` 메서드 사용
- 기존 메타데이터 구조 유지 (`answer`, `created_at`)
- 벡터 검색 없음 (순수 메타데이터 조회)

**검증 항목**:
```python
# 기존 계약 테스트에서 검증됨
def test_chromadb_get_returns_metadata():
    """ChromaDB get()이 documents와 metadatas를 반환하는지 검증"""
    ...
```

### 2. 관리자 인증 계약 (기존)

**위치**: `src/services/auth_service.py`

**내용**:
- 전역 관리자 상태 확인 (`is_admin_logged_in()`)
- 목록 조회는 인증된 관리자만 접근 가능

**검증 항목**:
```python
# 기존 인증 테스트에서 검증됨
def test_admin_authentication():
    """관리자 인증 상태 확인"""
    ...
```

### 3. Langfuse 추적 계약 (기존)

**위치**: `src/services/langfuse_service.py`

**내용**:
- 모든 목록 조회 작업은 Langfuse trace로 기록됨
- Trace 구조: `admin_list_qa_items` → spans (chromadb_get_all, sort_items, paginate)

**검증 항목**:
```python
# 통합 테스트에서 검증 예정
def test_list_items_creates_langfuse_trace():
    """목록 조회 시 Langfuse trace가 생성되는지 검증"""
    ...
```

## 내부 계약 (코드 레벨)

다음 내부 계약들은 data-model.md에 정의되어 있으며, 단위 테스트로 검증됩니다:

1. **QAListItem**: ChromaDB 결과 → 모델 변환
2. **PaginationState**: 페이징 로직 및 불변성
3. **ListViewState**: 뷰 상태 관리

**검증 파일**: `tests/unit/test_qa_list_models.py`

## 변경 불가 보장

이 기능은 다음을 변경하지 않습니다:

- ✅ ChromaDB 스키마 (기존 메타데이터 구조 유지)
- ✅ 관리자 인증 메커니즘
- ✅ init.txt 파일 형식
- ✅ Langfuse 추적 구조 (새 trace 타입 추가만)
- ✅ 기존 QAItem 모델

## 마이그레이션 필요 사항

**주의**: `created_at` 메타데이터 추가가 필요합니다.

- 기존 데이터: `created_at` 없음
- 신규 데이터: `created_at` 필수
- 마이그레이션: `data-model.md`의 마이그레이션 스크립트 참고

이는 **데이터 마이그레이션**이지 **계약 변경**은 아닙니다. 기존 계약(`answer` 메타데이터)은 유지됩니다.

## 헌법 준수 확인

**헌법 II: 벡터 인식 데이터 계약**

- ✅ 이 기능은 벡터 검색을 수행하지 않음
- ✅ 기존 ChromaDB 계약 준수
- ✅ 새로운 벡터 계약 불필요

## 결론

이 기능은 새로운 외부 계약을 도입하지 않으며, 기존 계약들을 그대로 활용합니다. 따라서 이 디렉토리는 비어있지만, 위의 기존 계약 문서들을 참조하면 됩니다.
