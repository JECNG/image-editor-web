# 이미지 수정 도구

웹 기반 이미지 수정 도구입니다. GitHub Pages로 배포하여 URL로 공유할 수 있습니다.

## 기능

- ✅ 이미지 크기 조정 (비율 유지)
- ✅ 배경 제거 (기본 기능)
- ✅ 다양한 형식 변환 (JPG, PNG, WEBP, GIF)
- ✅ 드래그 앤 드롭 지원
- ✅ 다중 파일 처리
- ✅ 실시간 미리보기

## 사용 방법

1. `image_editor_advanced.html` 파일을 GitHub 저장소에 업로드
2. GitHub Pages 설정:
   - 저장소 Settings → Pages
   - Source: Deploy from a branch
   - Branch: main (또는 master)
   - Folder: / (root)
3. 저장 후 몇 분 후 `https://[사용자명].github.io/[저장소명]/image_editor_advanced.html` 접속

## 파일 설명

- `image_editor.html`: 기본 버전
- `image_editor_advanced.html`: 고급 버전 (추천)

## 배경 제거 기능

현재는 클라이언트 사이드에서 기본적인 크기 조정만 수행합니다.
실제 배경 제거를 위해서는 서버 API가 필요합니다.

## 라이선스

자유롭게 사용 가능합니다.

