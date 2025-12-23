# Render.com 배경제거 백엔드 서버 설정 가이드

## 🔧 서비스 설정 (image-editor-web)

**Service ID**: `srv-d54j1i7gi27c73eb0tq0`

### 1. Build & Deploy 설정

#### Build Command
```
pip install -r requirements_image_backend.txt
```

#### Start Command
```
gunicorn image_bg_backend:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

**참고**: `--workers 1`은 Free 플랜의 메모리 제한을 고려한 설정입니다. `--timeout 120`은 모델 다운로드 및 이미지 처리 시간을 고려한 설정입니다.

### 2. Environment Variables (선택사항)

현재는 환경 변수가 필요 없지만, 나중에 필요하면 추가:

- `PYTHON_VERSION=3.11` (Python 버전 지정)
- `REMOVE_BG_MODEL=u2net` (기본값, 변경 불필요)

### 3. 수동 설정 방법

1. Render 대시보드 접속: https://dashboard.render.com
2. `image-editor-web` 서비스 클릭
3. **Settings** 탭 클릭
4. **Build & Deploy** 섹션에서:
   - **Build Command** 수정: `pip install -r github_release/requirements_image_backend.txt`
   - **Start Command** 수정: `cd github_release && gunicorn image_bg_backend:app --bind 0.0.0.0:$PORT`
5. **Save Changes** 클릭
6. **Manual Deploy** → **Clear cache & deploy** 실행

### 4. 배포 완료 후

배포가 성공하면:
- 서비스 URL 확인: `https://image-editor-web.onrender.com`
- Health 체크: `https://image-editor-web.onrender.com/api/health`
- API 엔드포인트: `https://image-editor-web.onrender.com/api/remove_bg`

### 5. HTML 파일 업데이트

배포 완료 후 `image_editor_with_tabs.html`의 API URL을 업데이트:

```javascript
const REMOVE_BG_API_URL = 'https://image-editor-web.onrender.com/api/remove_bg';
```

## ⚠️ 주의사항

1. **Free 플랜 제한**: 
   - 15분 비활성 시 자동 sleep
   - 첫 요청 시 약 30초 지연 (sleep에서 깨어남)
   
2. **메모리 제한**: 
   - Free 플랜: 512MB RAM
   - `rembg` 모델 로딩 시 메모리 사용량이 높을 수 있음

3. **타임아웃**: 
   - 이미지 처리 시간이 길면 타임아웃 발생 가능
   - 큰 이미지는 프론트엔드에서 크기 조정 후 전송 권장

## 📝 참고

- GitHub 저장소: https://github.com/JECNG/image-editor-web
- Python 런타임: 3.11+ 권장
- 필수 패키지: `requirements_image_backend.txt` 참고

