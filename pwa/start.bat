@echo off
title Ba Nghin Tu
cd /d "%~dp0"
echo.
echo   Dang khoi dong... giu cua so nay mo trong luc hoc.
echo.
start "" http://localhost:8777/
python -m http.server 8777 --bind 127.0.0.1 >nul 2>&1
if errorlevel 1 echo   Khong tim thay Python. Hay cai Python roi chay lai.
pause
