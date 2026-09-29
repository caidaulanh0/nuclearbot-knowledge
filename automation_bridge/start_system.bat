@echo off
chcp 65001 >nul
title Antigravity Physics AI System

echo ========================================================
echo       KHỞI ĐỘNG HỆ THỐNG TRỢ LÝ AI VẬT LÝ HẠT NHÂN
echo ========================================================
echo.

cd /d "D:\dulieutraning\automation_bridge"

:: 1. Kiểm tra Ollama
echo [1/3] Kiểm tra dịch vụ Ollama...
tasklist /fi "imagename eq ollama.exe" 2>NUL | find /i "ollama.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo    - Ollama đang chạy sẵn sàng.
) else (
    echo    - Đang khởi động Ollama...
    start "" ollama serve
    timeout /t 3 >nul
)

:: 2. Khởi động Qdrant trong WSL2 qua systemd
echo [2/3] Khởi động Vector Database Qdrant (WSL2)...
wsl -u root -e bash -c "systemctl is-active --quiet qdrant || systemd-run --unit=qdrant --uid=physics --gid=physics --working-directory=/home/physics/qdrant /home/physics/qdrant/qdrant"
timeout /t 2 >nul
echo    - Qdrant đã sẵn sàng tại http://localhost:6333.

:: 3. Mở trình duyệt Web
echo [3/3] Đang mở giao diện Chat trên trình duyệt...
start "" "http://localhost:7860"

:: 4. Chạy Web Server
echo.
echo ========================================================
echo    MÁY CHỦ CHAT SERVER ĐANG CHẠY TẠI http://localhost:7860
echo    (Nhấn Ctrl+C để dừng hệ thống khi không sử dụng)
echo ========================================================
echo.

.\venv\Scripts\python.exe src\chat_server.py

pause
