# 빠른 시작 가이드 (Quick Start)

5분 안에 QA Chat을 시작하세요!

---

## 📦 필수 요구사항

- **Python 3.12+** - [다운로드](https://www.python.org/)
- **Git** - [다운로드](https://git-scm.com/)

---

## 🚀 1단계: 프로젝트 다운로드

```bash
# 저장소 클론
git clone https://github.com/username/qa-chat.git
cd qa-chat
```

---

## 🔧 2단계: 환경 설정

### Windows

```powershell
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
.\venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt
```

### macOS/Linux

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

---

## ⚙️ 3단계: 환경 변수 설정

```bash
# .env 파일 생성 (복사)
cp .env.example .env
```

기본 설정으로 충분합니다. 필요하면 수정하세요:

```ini
ADMIN_PASSWORD=1234  # 관리자 패스워드
LOG_LEVEL=INFO       # 로그 레벨
```

---

## ▶️ 4단계: 앱 실행

```bash
python src/main.py
```

**예상 출력**:
```
INFO     root:main.py:50   === QA Chat Application Started ===
INFO     root:main.py:52   ✓ Initial load successful: 0 items loaded in 0.12ms
Launching Gradio interface...
Running on local URL:  http://127.0.0.1:7860
```

브라우저에서 `http://localhost:7860` 방문

---

## 💬 앱 사용법

### 사용자 탭 (첫 번째 탭)

1. "질문을 입력해주세요" 상자에 질문 입력
2. 예: "Python이란 무엇인가요?"
3. 답변이 자동으로 표시됨
4. 검색 결과가 없으면 정확히 `답변을 찾을 수 없습니다` 표시

### 관리자 탭 (두 번째 탭)

#### 로그인

1. 패스워드 입력 (기본값: `1234`)
2. 로그인 버튼 클릭
3. Q&A 관리 폼 표시

#### Q&A 추가/수정

1. 로그인 후
2. 질문 입력 (최대 500자)
3. 답변 입력 (최대 2000자)
4. 저장 버튼 클릭
5. "Q&A 추가되었습니다" 또는 "수정되었습니다" 메시지 표시

---

## 🧪 테스트 실행

모든 테스트 실행:

```bash
pytest tests/ -v
```

**예상 결과**:
```
======================== 94 passed in 8.96s =========================
```

특정 테스트만 실행:

```bash
# 단위 테스트
pytest tests/unit/ -v

# 인증 테스트
pytest tests/unit/test_auth.py -v

# 특정 테스트 함수
pytest tests/unit/test_auth.py::test_verify_password_with_correct_password -v
```

---

## 📁 초기 데이터 준비 (선택사항)

### JSON 파일에서 Q&A 추가

`data/init.txt` 파일을 만들고 줄 단위 JSON 추가:

```json
{"question": "Python이란 무엇인가요?", "answer": "Python은 높은 수준의 프로그래밍 언어입니다.", "metadata": {"source": "admin"}}
{"question": "Gradio는 뭔가요?", "answer": "Gradio는 Python 기반 웹 UI 라이브러리입니다.", "metadata": {"source": "admin"}}
```

앱을 재시작하면 자동으로 로드됩니다.

---

## 🔍 주요 폴더 구조

```
qa-chat/
├── src/              # 소스 코드
│   ├── main.py       # 메인 앱
│   ├── config.py     # 설정
│   ├── models/       # 데이터 모델
│   └── services/     # 비즈니스 로직
├── tests/            # 테스트 코드
├── data/
│   └── init.txt      # Q&A 데이터 (생성 후)
├── .chroma/          # ChromaDB 저장소 (생성 후)
├── .env              # 환경 변수 (생성 후)
└── README.md         # 전체 문서
```

---

## 🆘 문제 해결

### 문제: 프로젝트 시작이 느림

**해결**:
```bash
# 첫 실행 시 임베딩 모델 다운로드 (100-200MB)
# 이후 실행은 빠름
```

### 문제: "CUDA 없음" 경고 메시지

**해결**: 무시해도 됩니다. CPU 모드로 자동 전환.

### 문제: 포트 7860이 이미 사용 중

**해결**:
```bash
# 다른 포트로 실행하려면 (매우 고급)
# src/main.py 마지막 줄 수정: app.launch(share=False, server_port=7861)
```

### 문제: 테스트 실패

**해결**:
```bash
# 기존 데이터 정리 후 재시도
rm -rf .chroma/
rm data/init.txt 2>/dev/null || true
pytest tests/ -v
```

---

## 📚 다음 단계

### 기본 사용

- ✅ 앱 실행
- ✅ 사용자 탭에서 질문 입력
- ✅ 관리자 탭에서 Q&A 추가

### 개발

- 📖 [README.md](README.md) - 전체 문서
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - 개발 기여 가이드
- 📝 [CHANGELOG.md](CHANGELOG.md) - 버전 이력

### 고급

```bash
# 커버리지 리포트 보기
pytest tests/ --cov=src --cov-report=html
# htmlcov/index.html 열기

# 타입 체크 (mypy 설치 필요)
pip install mypy
mypy src/

# 코드 포매팅 (black 설치 필요)
pip install black
black src/ tests/
```

---

## 💡 유용한 팁

### Tip 1: 데이터 초기화

```bash
# ChromaDB 초기화
rm -rf .chroma/

# Q&A 파일 초기화
rm data/init.txt

# 앱 재시작
python src/main.py
```

### Tip 2: 로그 레벨 변경

```bash
# .env 파일 수정
LOG_LEVEL=DEBUG  # 상세 로그
```

### Tip 3: 관리자 패스워드 변경

```bash
# .env 파일 수정
ADMIN_PASSWORD=my_new_password
```

---

## 🎯 첫 Q&A 추가 예시

**절차**:

1. 앱 실행: `python src/main.py`
2. `http://localhost:7860` 방문
3. "관리자" 탭 선택
4. 패스워드 입력: `1234`
5. 로그인 클릭
6. 질문 입력: "Python 학습 기간은?"
7. 답변 입력: "기초 학습에 3-6개월이 소요됩니다."
8. 저장 클릭
9. "Q&A 추가되었습니다" 메시지 확인
10. "사용자" 탭으로 이동
11. 질문 입력: "Python을 배우는 데 얼마나 걸리나요?"
12. 답변이 표시됨!

---

## 🤔 자주 묻는 질문

**Q: 데이터는 어디에 저장되나요?**
A: `data/init.txt` 파일과 `.chroma/` 디렉토리에 저장됩니다.

**Q: 온라인에 배포할 수 있나요?**
A: 예, 향후 Docker/Heroku 가이드 예정.

**Q: 다른 사람들이 접근할 수 있나요?**
A: 로컬호스트만 접근. `share=True` 옵션으로 공개 링크 생성 가능.

**Q: 데이터를 백업하려면?**
A: `data/` 와 `.chroma/` 디렉토리 전체 복사.

---

## 📞 도움이 필요하신가요?

- 📖 [README.md](README.md) 전체 문서
- 🐛 [GitHub Issues](https://github.com/username/qa-chat/issues)
- 💬 [GitHub Discussions](https://github.com/username/qa-chat/discussions)

---

## ✅ 체크리스트

앱이 정상 작동하는지 확인:

- [ ] Python 3.12+ 설치
- [ ] `pip install -r requirements.txt` 완료
- [ ] `.env` 파일 생성
- [ ] `python src/main.py` 직행 (에러 없음)
- [ ] `http://localhost:7860` 접속 가능
- [ ] 테스트 통과: `pytest tests/ -v`

모두 확인되었나요? **축하합니다!** 🎉

**Happy Chatting! 🤖**
