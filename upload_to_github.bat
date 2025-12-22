@echo off
chcp 65001 >nul
echo ========================================
echo GitHub 저장소 업로드 스크립트
echo ========================================
echo.

REM 저장소 이름 설정
set REPO_NAME=image-editor-web
set GITHUB_USER=xuanh

echo 저장소 이름: %REPO_NAME%
echo GitHub 사용자: %GITHUB_USER%
echo.

REM 현재 디렉토리 확인
cd /d "%~dp0"
echo 현재 디렉토리: %CD%
echo.

REM Git 초기화 확인
if not exist ".git" (
    echo Git 저장소 초기화 중...
    git init
    git branch -M main
)

REM 파일 추가
echo 파일 추가 중...
git add .

REM 커밋
echo 커밋 중...
git commit -m "Initial commit: 이미지 수정 및 WEBP 변환 도구"

REM 원격 저장소 확인 및 추가
echo 원격 저장소 설정 중...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git

REM 푸시
echo.
echo ========================================
echo GitHub에 푸시 중...
echo ========================================
echo.
echo ⚠️  GitHub Personal Access Token이 필요합니다.
echo    사용자명: %GITHUB_USER%
echo    비밀번호 대신 Personal Access Token을 입력하세요.
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ 업로드 완료!
    echo ========================================
    echo.
    echo 저장소 URL: https://github.com/%GITHUB_USER%/%REPO_NAME%
    echo.
    echo GitHub Pages 설정:
    echo 1. https://github.com/%GITHUB_USER%/%REPO_NAME%/settings/pages 접속
    echo 2. Source: Deploy from a branch 선택
    echo 3. Branch: main, Folder: / (root) 선택
    echo 4. Save 클릭
    echo.
    echo 몇 분 후 다음 URL로 접속:
    echo https://%GITHUB_USER%.github.io/%REPO_NAME%/
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ 업로드 실패
    echo ========================================
    echo.
    echo 문제 해결:
    echo 1. GitHub Personal Access Token 확인
    echo 2. 저장소가 이미 존재하는지 확인
    echo 3. 저장소 이름을 변경하려면 REPO_NAME 변수 수정
    echo.
)

pause

