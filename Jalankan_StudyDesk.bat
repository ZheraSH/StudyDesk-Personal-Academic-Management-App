@echo off
title StudyDesk — Setup & Run
cd /d "%~dp0"

echo =======================================================
echo   StudyDesk — Personal Academic Management App
echo   Setup Environment Otomatis...
echo =======================================================
echo.

REM Cek apakah .venv sudah ada
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Membuat virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Python tidak ditemukan! Install Python 3.11+ dari python.org
        pause
        exit /b 1
    )
    echo [2/3] Menginstall dependensi (proses ini mungkin memakan beberapa menit)...
    .venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt flet flet-desktop >nul 2>&1
    echo [3/3] Setup selesai!
    echo.
) else (
    echo [OK] Virtual environment sudah ada. Langsung menjalankan aplikasi...
)

echo Membuka StudyDesk...
start "" ".venv\Scripts\pythonw.exe" main.py
exit
