# 기여 가이드 (Contributing Guide)

QA Chat 프로젝트에 기여해주셔서 감사합니다! 이 문서는 프로젝트에 기여하는 방법을 설명합니다.

---

## 기여 가능한 영역

- 🐛 **버그 수정**: 발견한 문제 해결
- ✨ **기능 개선**: 기존 기능 개선 또는 최적화
- 📚 **문서화**: README, docstring, 주석 개선
- 🧪 **테스트**: 테스트 커버리지 증가
- 🔄 **리팩토링**: 코드 품질 개선

---

## 개발 워크플로우

### 1단계: 환경 설정

```bash
# 저장소 포크
git clone <your-fork-url>
cd qa-chat

# 가상 환경 생성
python -m venv venv

# 활성화 (Windows)
.\venv\Scripts\activate

# 활성화 (macOS/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 개발 도구 추가 설치 (선택)
pip install black pylint mypy
```

### 2단계: 브랜치 생성

```bash
# 메인 브랜치 최신화
git fetch origin
git checkout main
git pull origin main

# 작업 브랜치 생성
git checkout -b feature/your-feature-name
# 또는
git checkout -b bugfix/issue-description
# 또는
git checkout -b docs/improvement
```

**브랜치 이름 규칙**:
- `feature/`: 새로운 기능 (예: `feature/user-auth`)
- `bugfix/`: 버그 수정 (예: `bugfix/search-error`)
- `docs/`: 문서 개선 (예: `docs/readme-update`)
- `test/`: 테스트 추가 (예: `test/add-coverage`)
- `refactor/`: 코드 리팩토링 (예: `refactor/service-layer`)

### 3단계: 코드 작성 (TDD)

#### 테스트 작성 먼저

```python
# tests/unit/test_new_feature.py
import pytest
from src.services.my_service import MyService

def test_my_feature_does_something():
    """목표: 내 기능은 ~를 수행한다"""
    service = MyService()
    result = service.do_something("input")
    
    assert result == "expected_output"
```

#### 테스트 실행 (빨강)

```bash
pytest tests/unit/test_new_feature.py -v
# FAILED: My feature is not implemented yet
```

#### 기능 구현

```python
# src/services/my_service.py
class MyService:
    def do_something(self, input_value):
        """설명을 여기에 작성
        
        Args:
            input_value: 입력값 설명
            
        Returns:
            반환값 및 타입
        """
        # 구현
        return "expected_output"
```

#### 테스트 실행 (초록)

```bash
pytest tests/unit/test_new_feature.py -v
# PASSED: My feature works!
```

#### 리팩토링 (필요시)

코드 정리 및 최적화

#### 전체 테스트 실행

```bash
pytest tests/ -v
# 모든 테스트 통과 확인
```

### 4단계: 커밋

```bash
# 변경사항 스테이징
git add .

# 또는 선택적 추가
git add src/services/my_service.py
git add tests/unit/test_new_feature.py

# 커밋 (명확한 메시지)
git commit -m "feat: add user authentication feature

- Implement login validation
- Add password hashing
- Add unit tests (8 tests)
"
```

**커밋 메시지 규칙** (주제 + 본문):

**주제** 형식:
```
<type>(<scope>): <subject>
```

예:
- `feat(auth): add password validation` - 새로운 기능
- `fix(search): handle empty query` - 버그 수정
- `docs(readme): update installation steps` - 문서화
- `test(auth): add edge case tests` - 테스트
- `refactor(services): simplify code structure` - 리팩토링

**본문** (선택사항, 상세 설명):
```
Longer explanation of what this commit does,
especially if there are tradeoffs or non-obvious
design decisions.

References: Closes #123 (이슈 번호 있으면)
```

### 5단계: 코드 품질 검증

```bash
# 모든 테스트 실행
pytest tests/ -v --cov=src

# 타입 체크 (설치 필요: pip install mypy)
mypy src/

# 코드 스타일 검사 (설치 필요: pip install black)
black --check src/ tests/

# 자동 포매팅
black src/ tests/
```

### 6단계: Push 및 Pull Request

```bash
# 브랜치 푸시
git push origin feature/your-feature-name

# GitHub에서 Pull Request 생성
# 또는 GitHub CLI 사용:
gh pr create --title "feat: add my feature" --body "Description of changes"
```

**PR 설명 템플릿**:

```markdown
## 변경 사항 요약
<!-- 간단한 설명 -->

## 타입
- [ ] 버그 수정
- [ ] 새로운 기능
- [ ] 문서화
- [ ] 리팩토링

## 관련 이슈
Closes #123 (이슈 번호 기입)

## 변경 사항 상세
- 무엇을 변경했는가
- 왜 변경했는가
- 어떻게 테스트했는가

## 테스트 결과
- [ ] 새로운 테스트 추가됨
- [ ] 기존 테스트 모두 통과
- [ ] 테스트 커버리지: %

```

### 7단계: 코드 리뷰

프로젝트 유지보수자가 코드를 검토하고 피드백을 제공합니다.

- 피드백에 따라 수정
- 재コミット 및 푸시
- "Ready for merge" 승인 대기

### 8단계: Merge

검토 완료 후 메인 브랜치에 병합됩니다.

---

## 코딩 스타일

### 파이썬 스타일 가이드

우리는 **PEP 8**을 준수합니다.

#### 타입 힌팅 (필수)

```python
# ❌ 나쁜 예
def search_qa(query, top_k):
    return results

# ✅ 좋은 예
from typing import List, Dict

def search_qa(query: str, top_k: int = 1) -> List[Dict]:
    """Q&A 검색
    
    Args:
        query: 검색어
        top_k: 반환할 최대 결과 수
        
    Returns:
        검색 결과 리스트
    """
    results = []
    # ...
    return results
```

#### Docstring (필수)

```python
class MyService:
    """서비스 설명
    
    메인 기능과 사용 방법 설명
    """
    
    def do_something(self, param: str) -> str:
        """메서드 설명 (한 줄)
        
        더 긴 설명이 필요하면 여기에 작성
        
        Args:
            param: 파라미터 설명
            
        Returns:
            반환값 설명
            
        Raises:
            ValueError: 언제 이 예외가 발생하는가
            
        Example:
            >>> service = MyService()
            >>> result = service.do_something("test")
            >>> print(result)
            "result"
        """
        pass
```

#### 로깅

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("디버그 정보")
    logger.info("주요 정보")
    logger.warning("경고")
    logger.error("에러 발생")
    logger.critical("심각한 에러")
```

#### 상수

```python
# ❌ 나쁜 예
MAX_LENGTH = 500
if len(question) > 500:
    pass

# ✅ 좋은 예
MAX_ADMIN_QUESTION_LENGTH = 500

if len(question) > MAX_ADMIN_QUESTION_LENGTH:
    pass
```

---

## 테스트 작성 가이드

### 유닛 테스트

```python
import pytest
from src.services.auth_service import AuthService

class TestAuthServiceValidation:
    """인증 서비스 검증 테스트"""
    
    def test_verify_password_with_correct_password(self):
        """목표: 올바른 패스워드는 인증 통과"""
        auth = AuthService()
        
        result = auth.verify_password("1234")
        
        assert result is True
    
    def test_verify_password_with_incorrect_password(self):
        """목표: 잘못된 패스워드는 인증 실패"""
        auth = AuthService()
        
        result = auth.verify_password("wrong")
        
        assert result is False
    
    def test_verify_password_with_empty_input(self):
        """목표: 빈 입력은 거부"""
        auth = AuthService()
        
        result = auth.verify_password("")
        
        assert result is False
```

### 테스트 네이밍 규칙

- **파일**: `test_*.py` 또는 `*_test.py`
- **클래스**: `Test*` (예: `TestAuthService`)
- **메서드**: `test_<what>_<scenario>_<expected>` (예: `test_verify_password_with_correct_password_returns_true`)

### Fixture 사용

```python
import pytest
import os

@pytest.fixture
def temp_data_file():
    """임시 데이터 파일"""
    filepath = "temp_test.txt"
    
    # 테스트 전
    yield filepath
    
    # 테스트 후 정리
    if os.path.exists(filepath):
        os.remove(filepath)

def test_save_data(temp_data_file):
    """테스트에서 임시 파일 사용"""
    # temp_data_file을 사용하여 테스트
    pass
```

---

## 문서화 시 주의사항

### README 수정 시

- 명확하고 간결한 한국어 또는 영어 사용
- 코드 예시는 실제 동작 가능한 예시로
- 문서 구조는 기존 구조 유지

### Docstring 작성 시

- 함수/클래스의 목적을 명확히
- Args와 Returns는 필수
- 복잡한 로직은 주석으로 설명

---

## PR 검토 체크리스트

PR을 제출하기 전에 다음을 확인하세요:

- [ ] 테스트가 모두 작성되고 통과하는가?
- [ ] 기존 테스트도 모두 통과하는가?
- [ ] 코드에 타입 힌팅이 있는가?
- [ ] Docstring이 모든 공개 함수에 있는가?
- [ ] 커밋 메시지가 명확한가?
- [ ] 불필요한 코멘트나 디버그 출력이 제거되었는가?
- [ ] 요구사항 문서를 업데이트했는가? (필요시)

---

## 리뷰어 가이드

### PR 리뷰 포인트

- [ ] 요구사항을 만족하는가?
- [ ] 테스트가 충분한가?
- [ ] 코드가 읽기 쉬운가?
- [ ] 성능상 문제는 없는가?
- [ ] 보안 문제는 없는가?
- [ ] 기존 코드와 일관성이 있는가?

---

## 문제가 있을 때

### 버그 보고

GitHub Issues에서:

```markdown
## 버그 설명
~를 입력했을 때 ~가 발생했습니다.

## 재현 방법
1. ~를 실행
2. ~를 입력
3. ~를 클릭

## 예상 동작
~가 되어야 합니다.

## 실제 동작
~가 됩니다.

## 환경
- OS: Windows/macOS/Linux
- Python 버전: 3.12
- 설치 방법: pip install -r requirements.txt
```

### 기능 요청

GitHub Discussions에서 논의 후 이슈로 변환

---

## 좋은 기여 예시

1. **작고 집중된 변경**: 한 번에 여러 기능을 넣지 말 것
2. **명확한 커밋 메시지**: 변경 사항을 쉽게 이해할 수 있도록
3. **완전한 테스트**: 새 코드는 항상 테스트와 함께
4. **기존 코드 존중**: 코드 스타일과 구조 일관성 유지

---

## 질문이 있을 때

- **일반 질문**: GitHub Discussions
- **기술 질문**: GitHub Issues (라벨: question)
- **긴급 이슈**: 프로젝트 유지보수자에게 직접 연락

---

## 마지막으로

이 프로젝트에 기여해주셔서 감사합니다! 🎉

당신의 기여는 모두에게 도움이 됩니다. 질문이나 어려움이 있으면 언제든지 물어보세요.

**Happy Coding! 🚀**
