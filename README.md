---
title: Chat Test
emoji: 🚀
colorFrom: gray
colorTo: purple
sdk: gradio
sdk_version: 6.8.0
app_file: app.py
pinned: false
license: mit
short_description: chat-test
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
# QA Chat 🤖

Gradio 기반 대화형 Q&A 챗봇 애플리케이션입니다. 사용자는 질문을 입력하여 답변을 검색하고, 관리자는 Q&A 데이터를 관리할 수 있습니다.

**MVP 구현 완료**: 4개 사용자 스토리, 94개 테스트 통과 ✅

---

## 📋 목차

- [기술 스택](#기술-스택)
- [시스템 요구사항](#시스템-요구사항)
- [설치 방법](#설치-방법)
- [환경 변수](#환경-변수)
- [실행 방법](#실행-방법)
- [개발 및 테스트](#개발-및-테스트)
- [프로젝트 구조](#프로젝트-구조)
- [주요 기능](#주요-기능)
- [아키텍처](#아키텍처)
- [개발 가이드라인](#개발-가이드라인)

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| **언어** | Python 3.12+ |
| **UI** | Gradio 4.26.0+ |
| **벡터 DB** | ChromaDB 0.4.24+ |
| **관찰성** | Langfuse 2.12.0+ |
| **테스트** | pytest 7.4.3+ |
| **환경 관리** | python-dotenv 1.0.0+ |
| **임베딩** | LangChain (HuggingFace기본) |

---

## 시스템 요구사항

- **OS**: Windows, macOS, Linux
- **Python**: 3.12 이상
- **메모리**: 최소 2GB (ChromaDB + 임베딩 모델)
- **저장 공간**: 최소 500MB (초기 설치)

---

## 설치 방법

### 1. 저장소 클론 및 디렉토리 이동

```bash
git clone <repository-url>
cd qa-chat
```

### 2. 가상 환경 생성 및 활성화

**Windows (PowerShell)**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD)**:
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux**:
```bash
python -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
cp .env.example .env  # 또는 아래 내용으로 새 파일 생성
```

자세한 내용은 [환경 변수](#환경-변수) 섹션 참고.

---

## 환경 변수

`.env` 파일에 다음 변수들을 설정하세요:

```ini
# 관리자 인증
ADMIN_PASSWORD=1234

# 검색 설정
SIMILARITY_THRESHOLD=0.7
MAX_USER_QUESTION_LENGTH=1024
MAX_ADMIN_QUESTION_LENGTH=500
MAX_ADMIN_ANSWER_LENGTH=2000

# 데이터 저장소
DATA_DIR=./data
INIT_FILE_PATH=./data/init.txt
CHROMA_PERSIST_DIR=./.chroma

# Langfuse (관찰성) - 선택사항
LANGFUSE_API_KEY=pk_...
LANGFUSE_SECRET_KEY=sk_...
LANGFUSE_PUBLIC_KEY=pk_...
LANGFUSE_HOST=https://cloud.langfuse.com

# 로깅
LOG_LEVEL=INFO
```

### 환경 변수 설명

| 변수 | 기본값 | 설명 |
|------|-------|------|
| `ADMIN_PASSWORD` | `1234` | 관리자 로그인 패스워드 |
| `SIMILARITY_THRESHOLD` | `0.7` | 검색 결과 유사도 임계값 (0~1) |
| `LOG_LEVEL` | `INFO` | 로깅 레벨 (DEBUG, INFO, WARNING, ERROR) |

> **⚠️ 주의**: `ADMIN_PASSWORD`는 개발 환경에서만 사용. 운영 환경에서는 더 강력한 인증 방식 사용 필수.
>
> **운영 메모**: 현재 관리자 인증 상태는 전역 단일 상태입니다. 하나의 클라이언트가 로그인하면 동일 앱 인스턴스에서 관리자 기능이 활성화될 수 있으므로, 운영 환경에서는 네트워크 접근 제어 및 강한 인증 정책을 함께 적용하세요.

---

## 실행 방법

### 로컬 환경에서 실행 (권장)

```bash
# 프로젝트 루트에서 실행
python app.py
```

또는 구 방식:

```bash
python src/main.py
```

그러면 Gradio 인터페이스가 자동으로 시작되며, 기본 URL은 `http://localhost:7860`입니다.

### Docker로 실행

```bash
# Docker 이미지 빌드
docker build -t qa-chat .

# 컨테이너 실행
docker run -p 7860:7860 \
  -e ADMIN_PASSWORD=1234 \
  -e SIMILARITY_THRESHOLD=0.7 \
  qa-chat
```

### Docker Compose로 실행

```bash
docker-compose up
```

### 공유 링크와 함께 실행

```bash
python -c "from src.main import QAChatApp; import asyncio; app = QAChatApp(); asyncio.run(app.on_startup()); app.launch(share=True)"
```

> **참고**: `share=True`일 때는 공개 URL이 생성되지만, 보안 주의 필요.

---

## 🚀 Hugging Face Spaces 배포

### 배포 구조 확인

이 프로젝트는 Hugging Face Spaces 배포에 최적화되어 있습니다:

- ✅ `app.py` - 루트 디렉토리의 엔트리포인트
- ✅ `requirements.txt` - 의존성 명시
- ✅ `.gitignore` - 불필요한 파일 제외
- ✅ `README.md` - 메타데이터 포함

### 배포 단계

1. **Hugging Face 저장소 생성**
   - [Hugging Face Hub](https://huggingface.co/spaces)에서 새 Space 생성
   - Owner 선택 > 저장소 이름 입력 > Space 생성

2. **저장소 설정 (README.md 메타데이터)**
   ```yaml
   ---
   title: QA Chat
   emoji: 🚀
   colorFrom: gray
   colorTo: purple
   sdk: gradio
   sdk_version: 6.8.0
   app_file: app.py
   pinned: false
   license: mit
   ---
   ```
   > 현재 README.md 상단에 이미 설정되어 있습니다.

3. **코드 푸시**
   ```bash
   git remote add huggingface https://huggingface.co/spaces/{username}/{space-name}
   git push huggingface main
   ```

4. **환경 변수 설정**
   - Space 설정(⚙️) → Secrets and variables
   - 다음 변수 추가:
     ```
     ADMIN_PASSWORD=<strong-password>
     SIMILARITY_THRESHOLD=0.7
     LANGFUSE_API_KEY=<your-api-key> (선택사항)
     ```

5. **배포 확인**
   - Space가 자동으로 빌드 및 배포됨
   - `https://huggingface.co/spaces/{username}/{space-name}`에서 확인

### 배포 후 데이터 관리

**데이터 초기화:**
- `data/init.txt`에 Q&A 데이터 추가
- 다음 포맷으로 저장 (JSON Lines):
  ```json
  {"question": "질문1", "answer": "답변1"}
  {"question": "질문2", "answer": "답변2"}
  ```

**지속성:**
- ChromaDB 데이터는 Space 재시작 시 초기화됨
- 영구 저장을 위해 HF datasets 또는 외부 DB 연동 필요

### 트러블슈팅

**문제**: 관리자 기능이 작동하지 않음
- **해결**: Secrets에서 `ADMIN_PASSWORD` 올바르게 설정 확인

**문제**: 데이터가 로드되지 않음
- **해결**: `data/init.txt` 파일 존재 및 형식 확인 (JSON Lines)

**문제**: 느린 응답 속도
- **해결**: 서버 스펙 업그레이드 또는 유사도 임계값 조정

---

## 개발 및 테스트

### 전체 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/ -v

# 커버리지 리포트 포함
pytest tests/ -v --cov=src --cov-report=html
```

### 특정 테스트만 실행

```bash
# 단위 테스트만
pytest tests/unit/ -v

# 통합 테스트만
pytest tests/integration/ -v

# 특정 파일
pytest tests/unit/test_auth.py -v

# 특정 테스트 함수
pytest tests/unit/test_auth.py::test_verify_password -v
```

### 테스트 커버리지 보기

```bash
pytest --cov=src --cov-report=html
# 참고: htmlcov/index.html에서 상세 리포트 확인
```

### 개발 중 테스트 감시 (파일 변경 시 자동 실행)

```bash
pytest tests/ -v --tb=short -x  # -x: 첫 실패 시 중단
```

---

## 프로젝트 구조

```
qa-chat/
├── app.py                          # Hugging Face Spaces 엔트리포인트
├── src/
│   ├── models/
│   │   └── qa_item.py              # Q&A 데이터 모델
│   ├── services/
│   │   ├── init_loader.py          # 초기 데이터 로드
│   │   ├── auth_service.py         # 관리자 인증
│   │   ├── file_service.py         # 파일 I/O (init.txt)
│   │   ├── embedding_service.py    # 텍스트 임베딩
│   │   ├── chromadb_service.py     # 벡터 DB 관리
│   │   ├── qa_update_service.py    # Q&A 추가/수정
│   │   ├── user_search_service.py  # 질문 검색
│   │   └── langfuse_service.py     # 관찰성 로깅
│   ├── main.py                     # Gradio 메인 앱 (핵심 로직)
│   └── config.py                   # 설정 관리
├── tests/
│   ├── unit/                       # 단위 테스트
│   ├── integration/                # 통합 테스트
│   └── contract/                   # 계약 테스트
├── data/
│   └── init.txt                    # Q&A 데이터 (줄 단위 JSON)
├── .chroma/                        # ChromaDB 저장소
├── requirements.txt                # 의존성 명세
├── pytest.ini                      # pytest 설정
├── Dockerfile                      # Docker 이미지 정의
├── docker-compose.yml              # Docker Compose 설정
├── .env                            # 환경 변수 (미포함)
├── .env.example                    # 환경 변수 템플릿
├── .gitignore                      # git 무시 파일
├── .dockerignore                   # Docker 무시 파일
└── README.md                       # 이 파일

```

---

## 주요 기능

### US1: 초기 데이터 로드 ✅

앱 시작 시 `data/init.txt`의 Q&A 데이터를 ChromaDB에 로드합니다.

- **파일 형식**: 줄 단위 JSON
- **속도**: 1000개 항목 ~100ms
- **자동 로드**: 앱 시작 시 자동 수행

### US2: 관리자 로그인 ✅

패스워드(기본값: `1234`)를 입력하여 관리자 인증합니다.

```
패스워드: 1234
→ [승인] 관리자 패널 표시
```

### US3: Q&A 관리 (추가/수정) ✅

관리자가 질문과 답변을 추가하거나 수정할 수 있습니다.

- **입력 제한**:
  - 질문: 최대 500자
  - 답변: 최대 2000자
- **중복 처리**: 기존 질문은 자동으로 덮어씀

### US4: 사용자 질문 검색 ✅

사용자 질문에 대해 ChromaDB 유사 검색을 수행합니다.

- **결과 없음 고정 문구**: `답변을 찾을 수 없습니다`
- **검색 기준**: 유사도 임계값 0.7, 상위 1개 결과
- **즉시 반영**: ChromaDB에 실시간 업데이트

### US4: 질문 답변 (검색) ✅

사용자가 질문을 입력하면 유사도 기반으로 답변을 검색합니다.

- **검색 방식**: 임베딩 벡터 유사도
- **임계값**: 0.7 이상만 반환 (FR-004)
- **결과**: 최대 1개 (FR-009)
- **지연**: ~100-200ms

---

## 아키텍처

### 계층 구조

```
┌─────────────────────────────────────┐
│  Gradio UI (main.py)                │ ← 사용자/관리자 인터페이스
├─────────────────────────────────────┤
│  Services Layer                     │
│  ├─ AuthService (US2)               │
│  ├─ QAUpdateService (US3)           │
│  ├─ UserSearchService (US4)         │
│  └─ InitLoader (US1)                │
├─────────────────────────────────────┤
│  Data Layer                         │
│  ├─ ChromaDBService (벡터 검색)      │
│  ├─ FileService (파일 I/O)          │
│  └─ EmbeddingService (임베딩 생성)   │
├─────────────────────────────────────┤
│  Storage                            │
│  ├─ data/init.txt (Q&A 저장소)      │
│  └─ .chroma/ (벡터 인덱스)           │
└─────────────────────────────────────┘
```

### 데이터 흐름

**사용자 질문 검색**:
```
사용자 입력
   ↓
search_answer()
   ↓
UserSearchService.search_qa()
   ↓
ChromaDBService.search_similar()
   ↓
EmbeddingService (코사인 유사도)
   ↓
Langfuse 로깅
   ↓
결과 반환 (상위 1개)
```

**관리자 Q&A 추가**:
```
관리자 입력 + 로그인 확인
   ↓
QAUpdateService.add_or_update_qa()
   ├─ validate_input() (길이 검증)
   ├─ FileService.update_or_insert_qa_item() (파일 저장)
   ├─ ChromaDBService.update_qa_item() (색인 업데이트)
   └─ Langfuse 로깅
   ↓
성공 메시지 반환
```

---

## 개발 가이드라인

### TDD 원칙

모든 기능은 테스트 먼저 작성 후 구현:

```bash
# 1. 테스트 작성 (tests/unit/test_feature.py)
# 2. 테스트 실행 → 실패 확인
pytest tests/unit/test_feature.py -v

# 3. 기능 구현 (src/services/feature.py)
# 4. 테스트 재실행 → 통과 확인
pytest tests/unit/test_feature.py -v

# 5. 통합 테스트 추가 및 실행
```

### 서비스 싱글톤 패턴

모든 주요 서비스는 싱글톤 팩토리 함수 제공:

```python
from src.services.chromadb_service import get_chromadb_service

# 애플리케이션 전체에서 동일한 인스턴스 사용
chroma = get_chromadb_service()
```

### Langfuse 로깅

주요 액션은 Langfuse에 로깅:

```python
from src.services.langfuse_service import get_langfuse_service

langfuse = get_langfuse_service()

# 검색 로깅
langfuse.log_user_search(
    question_length=len(query),
    num_results=len(results),
    top_similarity=results[0]['similarity'] if results else 0.0
)
```

### 코딩 스타일

- **포매팅**: Black (자동 포매팅은 미설정, 수동 준수)
- **타입 힌팅**: 모든 함수에 타입 힌팅 추가
- **문서화**: 함수/클래스에 docstring 기입
- **로깅**: 주요 지점에 logger.info/warning/error 추가

---

## FAQ

### Q: 초기 Q&A 데이터는 어디에 저장되나요?

**A**: `data/init.txt` 파일에 줄 단위 JSON 형식으로 저장됩니다.

```json
{"question": "What is Python?", "answer": "A programming language", "metadata": {}}
```

### Q: 검색 정확도를 개선하려면?

**A**: `.env`에서 `SIMILARITY_THRESHOLD` 값을 조정하세요:
- `0.7` (기본): 엄격한 필터링
- `0.6`: 더 많은 결과
- `0.8`: 더 정확한 결과

### Q: Langfuse 없이 실행할 수 있나요?

**A**: 예, `.env`에서 `LANGFUSE_API_KEY`를 설정하지 않으면 로컬 로깅만 사용됩니다.

### Q: 관리자 패스워드를 변경하려면?

**A**: `.env` 파일에서 `ADMIN_PASSWORD` 값을 변경하세요.

```ini
ADMIN_PASSWORD=my_new_password
```

### Q: ChromaDB 데이터를 초기화하려면?

**A**: `.chroma/` 디렉토리를 삭제한 후 앱을 다시 시작하면 새로 생성됩니다.

```bash
rm -rf .chroma/  # macOS/Linux
rmdir /s /q .chroma\  # Windows
```

---

## 성능 지표

| 작업 | 예상 시간 |
|------|---------|
| 앱 시작 | ~2초 |
| 100개 Q&A 초기 로드 | ~50ms |
| 사용자 검색 쿼리 | ~100-200ms |
| 관리자 Q&A 추가 | ~150-300ms |
| 테스트 전체 실행 | ~8초 (94개) |

---

## 테스트 현황

**전체 테스트**: 94개 ✅

| 카테고리 | 개수 | 상태 |
|---------|------|------|
| 단위 테스트 (Unit) | 48개 | ✅ Pass |
| 통합 테스트 (Integration) | 30개 | ✅ Pass |
| 계약 테스트 (Contract) | 16개 | ✅ Pass |
| **총합** | **94개** | **✅ Pass** |

---

## 개발 환경 샘플

### VS Code 설정 추천

`.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  }
}
```

### Pre-commit 훅 (선택사항)

```bash
# 설치
pip install pre-commit

# .pre-commit-config.yaml 작성 후
pre-commit install
```

---

## 다음 단계 (Phase 7+)

- [ ] 다중 사용자 지원
- [ ] 데이터베이스 마이그레이션 (SQLite/PostgreSQL)
- [ ] 관리자 대시보드 확장
- [ ] 성능 최적화 (캐싱, 배치 처리)
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인 (GitHub Actions)

---

## 라이선스

프로젝트 라이선스 정보를 입력하세요.

---

## 기여

버그 리포트와 기여는 언제나 환영합니다!

1. fork 하세요
2. feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

###기여 가이드라인

- 모든 새로운 기능은 테스트와 함께 제출
- 커밋 메시지는 명확하고 간결하게
- Python 타입 힌팅 필수
- docstring 기입 필수

---

## 연락처 및 지원

- **문제 리포트**: GitHub Issues
- **기술 논의**: GitHub Discussions
- **이메일**: support@example.com

---

## 변경 이력

**v1.0.0** (2026-03-03)
- MVP 릴리스
- 4개 사용자 스토리 구현 완료
- 94개 테스트 통과

---

**마지막 업데이트**: 2026-03-03

Happy Coding! 🚀
---
title: Chat Test
emoji: 🚀
colorFrom: gray
colorTo: purple
sdk: gradio
sdk_version: 6.8.0
app_file: app.py
pinned: false
license: mit
short_description: chat-test
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
