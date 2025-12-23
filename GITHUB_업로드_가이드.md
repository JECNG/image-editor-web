# GitHub 업로드 가이드

## ✅ 이 폴더의 파일들

이 `github_release` 폴더에는 GitHub에 올릴 파일들만 정리되어 있습니다.

## 📦 포함된 파일

- ✅ HTML 파일들 (이미지 에디터)
- ✅ 백엔드 서버 코드
- ✅ 문서 파일들
- ✅ 설정 파일들 (.gitignore, requirements)

## 🚀 GitHub 업로드 방법

### 1. Git 초기화 (처음만)

```bash
cd github_release
git init
git add .
git commit -m "Initial commit: Image editor with backend"
```

### 2. GitHub 저장소 생성

1. GitHub에서 새 저장소 생성
2. 저장소 URL 복사

### 3. 원격 저장소 연결 및 푸시

```bash
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

## 🌐 GitHub Pages 설정

1. 저장소 Settings → Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: / (root)
5. Save

그 다음 `https://your-username.github.io/your-repo/image_editor_with_tabs.html` 접속

## ⚠️ 중요 참고사항

- **백엔드 서버는 GitHub Pages에서 실행되지 않습니다**
- 이미지 수정 기능은 서버 없이 작동합니다
- WEBP 변환 기능은 별도 서버 호스팅이 필요합니다




