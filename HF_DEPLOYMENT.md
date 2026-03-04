# 🚀 Hugging Face Spaces 배포 체크리스트

Hugging Face Spaces에 배포하기 전에 확인하세요.

## ✅ 배포 준비 사항

### 필수 파일 확인

- [x] `app.py` - 프로젝트 루트의 엔트리포인트 (Hugging Face 필수)
- [x] `requirements.txt` - 의존성 명시 (프로젝트 루트)
- [x] `README.md` - 메타데이터 포함
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
- [x] `.gitignore` - 불필요한 파일 제외
- [x] `data/init.txt` - 초기 Q&A 데이터

### 환경 변수 설정

Hugging Face Space 설정에서 다음 변수를 추가하세요:

| 변수명 | 기본값 | 설명 | 필수여부 |
|--------|--------|------|---------|
| `ADMIN_PASSWORD` | `1234` | 관리자 로그인 패스워드 | ⚠️ 권장 (변경 필수) |
| `SIMILARITY_THRESHOLD` | `0.7` | 검색 유사도 임계값 | ⚠️ 권장 |
| `LANGFUSE_API_KEY` | (비어있음) | Langfuse 로깅 (선택) | ❌ 선택 |

**⚠️ 중요**: `ADMIN_PASSWORD`는 강력한 비밀번호로 변경하세요!

### 배포 단계

#### 1️⃣ Hugging Face Hub 계정 생성
- [Hugging Face](https://huggingface.co) 회원가입

#### 2️⃣ Space 생성
- [Spaces 대시보드](https://huggingface.co/spaces)에서 "Create new Space" 클릭
- 저장소 이름 입력 (예: `qa-chat`)
- Space type에서 **Gradio** 선택
- **License**: MIT 선택

#### 3️⃣ 코드 푸시
```bash
# 현재 프로젝트에서
git remote add huggingface https://huggingface.co/spaces/{username}/{space-name}
git push huggingface main
```

또는 GitHub Actions로 자동 동기화 설정 (선택사항)

#### 4️⃣ 환경 변수 설정
- Space 페이지 상단의 **Settings** (⚙️) 클릭
- **Secrets and variables** 섹션에서 변수 추가
- `ADMIN_PASSWORD` 입력 및 저장

#### 5️⃣ 배포 확인
- Space 페이지에서 자동 빌드 진행 상황 확인
- 완료 후 URL에서 애플리케이션 테스트

---

## 📊 배포 후 체크리스트

- [ ] 애플리케이션이 정상 로드되는지 확인
- [ ] 사용자 검색 기능 테스트
  - 질문 입력 → 답변 확인
- [ ] 관리자 로그인 테스트
  - 올바른 비밀번호로 로그인 확인
  - 잘못된 비밀번호로 로그인 거부 확인
- [ ] Q&A 추가 기능 테스트
  - 새로운 Q&A 추가 → 검색으로 확인
- [ ] 데이터 지속성 확인
  - 로그아웃 후 재로그인 시 데이터 유지 확인

---

## 🔧 트러블슈팅

### 문제: "404 Not Found" 또는 앱이 로드되지 않음

**원인**:
- `app.py` 파일이 프로젝트 루트가 아닌 다른 위치에 있음
- `requirements.txt`에 필수 패키지가 없음

**해결책**:
```bash
# 파일 위치 확인
ls app.py requirements.txt

# 필요하면 Git에 다시 푸시
git push huggingface main
```

### 문제: "Module not found" 에러

**원인**:
- 필수 패키지가 `requirements.txt`에 없음
- 패키지 버전 호환성 문제

**해결책**:
```bash
# requirements.txt 확인 및 업데이트
pip freeze > requirements.txt

# 다시 푸시
git push huggingface main
```

### 문제: 관리자 로그인 실패

**원인**:
- `ADMIN_PASSWORD` 환경 변수가 설정되지 않음
- 비밀번호 입력 오류

**해결책**:
1. Space Settings → Secrets and variables 확인
2. `ADMIN_PASSWORD` 재설정 및 저장
3. Space 페이지 새로고침

### 문제: 데이터가 로드되지 않음

**원인**:
- `data/init.txt` 파일이 없거나 형식 오류
- ChromaDB 저장소 초기화 문제

**해결책**:
```bash
# data/init.txt 형식 확인 (JSON Lines)
# 각 줄이 다음 형식이어야 함:
# {"question": "질문", "answer": "답변"}
```

---

## 📈 배포 후 모니터링

### 성능 지표

- **응답 시간**: 일반적으로 1-3초
- **동시 사용자**: Space 스펙에 따라 5-10명
- **메모리 사용**: 약 500MB-1GB

### Langfuse 통합 (선택사항)

관찰성을 위해 Langfuse를 설정할 수 있습니다:

1. [Langfuse](https://langfuse.com) 계정 생성
2. API 키 발급
3. Space Secrets에 `LANGFUSE_API_KEY` 추가
4. 대시보드에서 로그 모니터링

---

## 💡 팁

- **정기적 백업**: GitHub에 정기적으로 푸시하여 버전 관리
- **테스팅**: 로컬에서 `python app.py`로 테스트 후 배포
- **데이터 관리**: 중요한 Q&A는 정기적으로 백업
- **보안**: 운영 환경에서는 더 강력한 인증 메커니즘 고려

---

## 🔗 참고 자료

- [Hugging Face Spaces 공식 문서](https://huggingface.co/docs/hub/spaces)
- [Gradio 공식 문서](https://www.gradio.app/)
- [우리 프로젝트 README](./README.md)

---

**배포 완료!** 🎉

만약 문제가 있으면 [Issues](https://github.com/username/qa-chat/issues)에 보고해주세요.
