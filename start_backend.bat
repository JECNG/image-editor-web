@echo off
chcp 65001 >nul
echo ========================================
echo 백엔드 서버 시작
echo ========================================
echo.

REM 현재 디렉토리로 이동
cd /d "%~dp0"

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 필요한 패키지가 설치되어 있는지 확인
echo 필요한 패키지 확인 중...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Flask가 설치되어 있지 않습니다. 설치 중...
    pip install -r requirements_backend.txt
    if errorlevel 1 (
        echo [오류] 패키지 설치 실패
        pause
        exit /b 1
    )
)

REM FFmpeg 확인
echo.
echo FFmpeg 확인 중...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [경고] FFmpeg를 찾을 수 없습니다.
    echo FFmpeg가 설치되어 있지 않으면 변환이 작동하지 않습니다.
    echo FFmpeg 다운로드: https://ffmpeg.org/download.html
    echo.
    echo 계속하시겠습니까? (Y/N)
    set /p continue=
    if /i not "%continue%"=="Y" (
        exit /b 1
    )
) else (
    echo FFmpeg 확인 완료!
)

echo.
echo ========================================
echo 서버 시작 중...
echo ========================================
echo 서버 주소: http://localhost:5000
echo API 엔드포인트: http://localhost:5000/api/convert
echo.
echo 서버를 종료하려면 Ctrl+C를 누르세요.
echo ========================================
echo.

REM 서버 실행
python backend_server.py

pause

