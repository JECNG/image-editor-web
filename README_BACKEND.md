# 백엔드 서버 사용 가이드

## 📋 필요 사항

1. **Python 3.7+**
2. **FFmpeg** (시스템 PATH에 설치되어 있어야 함)
   - Windows: https://ffmpeg.org/download.html
   - 또는 `ffmpeg.exe`를 프로젝트 폴더에 배치

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements_backend.txt
```

### 2. FFmpeg 확인

FFmpeg가 설치되어 있는지 확인:
```bash
ffmpeg -version
```

만약 FFmpeg가 다른 경로에 있다면, 환경 변수 설정:
```bash
# Windows
set FFMPEG_PATH=C:\path\to\ffmpeg.exe

# Linux/Mac
export FFMPEG_PATH=/usr/bin/ffmpeg
```

### 3. 서버 실행

```bash
python backend_server.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## 📡 API 엔드포인트

### POST /api/convert

MP4 파일을 WEBP 또는 GIF로 변환합니다.

**요청:**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `file`: MP4 파일
  - `watermarkText`: 워터마크 텍스트 (선택)
  - `watermarkColor`: 워터마크 색상 (hex, 예: #FFFFFF)
  - `fontSize`: 폰트 크기 (기본: 24)
  - `opacity`: 투명도 (0.0-1.0, 기본: 0.5)
  - `position`: 워터마크 위치 (top-left, top-center, top-right, mid-left, mid-center, mid-right, bot-left, bot-center, bot-right)
  - `videoLength`: 영상 길이 (full, partial)
  - `startTime`: 시작 시간 (HH:MM:SS, videoLength가 partial일 때)
  - `endTime`: 종료 시간 (HH:MM:SS, videoLength가 partial일 때)
  - `width`: 출력 가로 크기 (px, 기본: 600)
  - `format`: 출력 형식 (webp, gif)

**응답:**
- 변환된 파일 (WEBP 또는 GIF)

### GET /api/health

서버 상태 확인

**응답:**
```json
{
  "status": "ok",
  "ffmpeg_available": true
}
```

## 🌐 HTML 파일 설정

`image_editor_with_tabs.html` 파일에서 API URL을 설정할 수 있습니다:

```javascript
// 기본값: http://localhost:5000/api/convert
const API_URL = 'http://localhost:5000/api/convert';
```

다른 서버를 사용하는 경우 이 값을 변경하세요.

## ⚠️ 문제 해결

### FFmpeg를 찾을 수 없음
- FFmpeg가 시스템 PATH에 있는지 확인
- 또는 `FFMPEG_PATH` 환경 변수 설정

### CORS 오류
- `flask-cors`가 설치되어 있는지 확인
- 서버가 `CORS(app)`로 설정되어 있는지 확인

### 변환 실패
- FFmpeg 로그 확인
- 입력 파일 형식 확인 (MP4만 지원)
- 파일 크기 및 해상도 확인

## 📝 참고사항

- 변환 시간은 파일 크기와 해상도에 따라 다릅니다
- 대용량 파일의 경우 타임아웃이 발생할 수 있습니다 (현재 5분)
- 임시 파일은 자동으로 정리됩니다

