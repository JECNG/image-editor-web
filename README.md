# 🖼️ 이미지 수정 & WEBP 변환 도구

웹 기반 이미지 수정 및 MP4 → WEBP/GIF 변환 도구입니다.

## ✨ 주요 기능

### 🖼️ 이미지 수정 탭
- ✅ 이미지 크기 조정 (비율 유지)
- ✅ 배경 제거 (브라우저에서 직접 처리)
- ✅ 다양한 형식 변환 (JPG, PNG, WEBP, GIF)
- ✅ 드래그 앤 드롭 지원
- ✅ 다중 파일 처리
- ✅ 실시간 미리보기

### 🎬 WEBP 변환 탭 (ffmpeg.wasm 사용)
- ✅ MP4 → WEBP 변환 (브라우저에서 직접 처리)
- ✅ MP4 → GIF 변환 (브라우저에서 직접 처리)
- ✅ 워터마크 추가 (텍스트, 색상, 크기, 투명도, 위치)
- ✅ 영상 구간 선택
- ✅ 해상도 조정
- ✅ **서버 불필요** - GitHub Pages에서 완전히 작동!

## 🚀 빠른 시작

### 방법 1: HTML 파일 직접 열기 (간단)

1. `image_editor_with_tabs.html` 파일을 브라우저에서 열기
2. **이미지 수정 탭**은 바로 사용 가능 (서버 불필요)
3. **WEBP 변환 탭**은 백엔드 서버 필요 (아래 참고)

### 방법 2: HTTP 서버로 실행 (권장)

```bash
# Python HTTP 서버 실행
python -m http.server 8000

# 브라우저에서 접속
# http://localhost:8000/image_editor_with_tabs.html
```

## 🔧 백엔드 서버 설정 (WEBP 변환 사용 시)

WEBP 변환 기능을 사용하려면 백엔드 서버가 필요합니다.

### 1. 의존성 설치

```bash
pip install -r requirements_backend.txt
```

### 2. FFmpeg 설치

- Windows: https://ffmpeg.org/download.html
- FFmpeg가 시스템 PATH에 있어야 합니다

### 3. 서버 실행

**Windows:**
```bash
start_backend.bat
```

**또는 직접 실행:**
```bash
python backend_server.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## 📁 파일 구조

```
github_release/
├── image_editor_with_tabs.html  # 메인 HTML 파일 (추천)
├── image_editor.html            # 기본 버전
├── image_editor_advanced.html   # 고급 버전
├── backend_server.py            # 백엔드 서버 (WEBP 변환용)
├── requirements_backend.txt     # Python 패키지 목록
├── start_backend.bat            # 서버 실행 스크립트 (Windows)
├── README.md                    # 이 파일
├── README_BACKEND.md            # 백엔드 상세 가이드
├── README_GITHUB.md             # GitHub Pages 배포 가이드
└── .gitignore                   # Git 제외 파일 목록
```

## 🌐 GitHub Pages 배포

### ✅ GitHub Pages에서 작동하는 버전

**`index.html` (또는 `image_editor_advanced.html`)** - **이 버전을 사용하세요!**
- ✅ **이미지 수정 기능**: 완전히 작동 (서버 불필요)
- ✅ **배경 제거**: 브라우저에서 직접 처리
- ✅ **형식 변환**: JPG, PNG, WEBP, GIF 모두 작동
- ✅ **GitHub Pages에서 바로 사용 가능**

**배포 방법:**
1. 이 폴더를 GitHub 저장소에 업로드
2. Settings → Pages → Source: main branch 선택
3. `https://your-username.github.io/your-repo/` 접속 (자동으로 index.html 열림)

### ⚠️ 서버가 필요한 버전

**`image_editor_with_tabs.html`** - WEBP 변환 탭 포함
- ✅ 이미지 수정 탭: 작동 (서버 불필요)
- ❌ WEBP 변환 탭: **작동 안 함** (백엔드 서버 필요)

**중요:** GitHub Pages는 정적 파일만 호스팅하므로 Python 백엔드 서버는 실행되지 않습니다.

WEBP 변환을 사용하려면:
- 백엔드 서버를 별도로 호스팅해야 합니다 (Heroku, Railway, Render 등)
- 또는 로컬에서 `start_backend.bat` 실행 후 사용

## 📖 상세 문서

- [백엔드 서버 사용 가이드](README_BACKEND.md)
- [GitHub Pages 배포 가이드](README_GITHUB.md)
- [GitHub 업로드 가이드](GITHUB_업로드_가이드.md)

## ⚠️ 주의사항

1. **CORS 오류**: 로컬 파일로 열면 CORS 오류가 발생할 수 있습니다. HTTP 서버로 실행하는 것을 권장합니다.

2. **백엔드 서버**: WEBP 변환 기능은 백엔드 서버가 실행 중이어야 작동합니다.

3. **FFmpeg**: WEBP 변환을 사용하려면 FFmpeg가 설치되어 있어야 합니다.

## 📝 라이선스

자유롭게 사용 가능합니다.

## 🤝 기여

이슈 및 풀 리퀘스트 환영합니다!

