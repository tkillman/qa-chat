# Contracts: Q&A 항목 삭제 기능

이 기능은 외부 공개 API를 새로 추가하지 않는다. 대신 내부 서비스/UI 이벤트 계약을 명시한다.

## 포함 문서

- `admin-delete-ui-contract.md`: 테이블 UI + 확인 다이얼로그 상호작용 계약
- `delete-request.md`: `QADeleteRequest` 입력 계약
- `delete-response.md`: `QADeleteResult` 출력 계약
- `qa-delete-service-contract.md`: `QADeleteService.delete_qa_item()` 동작 계약
