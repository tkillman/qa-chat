# Quickstart: Q&A 삭제 기능 검증

**기능**: Q&A 항목 삭제 기능 | **브랜치**: `002-delete-qa-item` | **난이도**: 중

---

## 📋 개요

이 가이드는 Q&A 삭제 기능을 빠르게 검증하고 테스트하는 방법을 설명합니다.

### 핵심 기능
- ✅ 관리자 목록 조회에서 각 항목마다 `🗑️ 삭제` 버튼 표시
- ✅ 삭제 버튼 클릭 시 "이 항목을 삭제하시겠습니까?" 확인 다이얼로그 표시  
- ✅ "예" 선택 시 ChromaDB에서 항목 삭제 + 목록 자동 갱신
- ✅ 모든 작업을 Langfuse로 추적

---

## 🔧 환경 준비

### 1. 작업 브랜치 확인

```bash
cd /c/fun/qa-chat
git branch  # 현재 002-delete-qa-item에 있어야 함
```

### 2. 가상환경 활성화

**Windows PowerShell:**
```powershell
& C:/fun/qa-chat/.venv/Scripts/Activate.ps1
```

**Git Bash:**
```bash
source .venv/Scripts/activate
```

### 3. 의존성 확인

```bash
pip install -r requirements.txt
```

---

## ✅ 단계별 검증

### 단계 1: 단위 테스트 (코드 검증)

```bash
python -m pytest tests/unit/test_qa_delete_service.py -v
```

### 단계 2: 수동 테스트 (UI 검증)

#### 2.1 앱 시작

```bash
python src/main.py
```

#### 2.2 관리자 로그인

1. **관리자** 탭에서 비밀번호 `1234` 입력
2. **로그인** 클릭

#### 2.3 목록 조회 탭 진입

1. **관리자** → **📋 목록 조회**
2. 각 카드 우측에 **🗑️ 삭제** 버튼 확인

#### 2.4 삭제 플로우 테스트

1. **🗑️ 삭제** 클릭
2. "이 항목을 삭제하시겠습니까?" 메시지 표시 확인
3. **예** 클릭
4. 토스트 메시지: "✓ 삭제되었습니다" 확인
5. 해당 항목이 목록에서 제거 확인

---

## 📊 검증 체크리스트

| 기능 | 상태 |
|------|:--:|
| 버튼 표시 | ⬜ |
| 다이얼로그 표시 | ⬜ |
| 삭제 실행 | ⬜ |
| 목록 갱신 | ⬜ |
| Langfuse 기록 | ⬜ |

---

## 📚 참고 문서

- [데이터 모델](../data-model.md)
- [API 계약](../contracts/)
- [스펙](../spec.md)
- [구현 계획](../plan.md)
