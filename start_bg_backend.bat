@echo off
chcp 65001 >nul
title 배경제거 백엔드 서버
color 0A

echo ========================================
echo 배경제거 백엔드 서버 시작
echo ========================================
echo.

REM 현재 스크립트 위치로 이동
cd /d "%~dp0"

REM Python 설치 확인
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 설치한 후 다시 시도해주세요.
    pause
    exit /b 1
)

REM 필요한 패키지 확인
echo 필요한 패키지 확인 중...
python -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [경고] Flask가 설치되어 있지 않습니다.
    echo 자동으로 설치하시겠습니까? (Y/N)
    set /p install="> "
    if /i "%install%"=="Y" (
        echo 패키지 설치 중...
        pip install flask flask-cors pillow rembg numpy opencv-python scikit-image pymatting
        if %ERRORLEVEL% NEQ 0 (
            echo [오류] 패키지 설치 실패
            pause
            exit /b 1
        )
    ) else (
        echo 설치를 취소했습니다.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 서버 시작 중...
echo ========================================
echo.
echo 서버 주소: http://localhost:5001
echo API 엔드포인트: http://localhost:5001/api/remove_bg
echo.
echo 서버를 종료하려면 Ctrl+C를 누르세요.
echo.
echo ========================================
echo.

REM 서버 실행
python image_bg_backend.py

REM 서버 종료 시
echo.
echo 서버가 종료되었습니다.
pause

