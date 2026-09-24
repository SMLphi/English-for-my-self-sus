@echo off
REM Dung lai toan bo app: du lieu -> ban claude.ai -> ban PWA deploy duoc
cd /d "%~dp0"
setlocal
set PYTHONIOENCODING=utf-8

echo.
echo [1/4] Ghep anh thanh sprite...
python build\sprites.py || goto :err

echo.
echo [2/4] Dung du lieu va nhung vao HTML...
python build\build.py || goto :err

echo.
echo [3/4] Tao icon...
python build\make_icons.py || goto :err

echo.
echo [4/4] Dung ban PWA (thu muc pwa\)...
python build\make_pwa.py || goto :err

echo.
echo === XONG. Thu muc "pwa" da san sang de deploy. ===
goto :eof

:err
echo.
echo *** BUILD LOI ***
exit /b 1
