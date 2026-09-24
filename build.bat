@echo off
REM Dung lai toan bo app: du lieu -> ban claude.ai -> ban PWA deploy duoc
cd /d "%~dp0"
setlocal
set PYTHONIOENCODING=utf-8

echo.
if not exist "build\fonts\fonts.css" (
  echo [0/5] Tai phong chu ve de tu host...
  python build\get_fonts.py || goto :err
  echo.
)

echo [1/5] Ghep anh thanh sprite...
python build\sprites.py || goto :err

echo.
echo [2/5] Dung du lieu va nhung vao HTML...
python build\build.py || goto :err

echo.
echo [3/5] Tao icon...
python build\make_icons.py || goto :err

echo.
echo [4/5] Dung ban PWA (thu muc pwa\)...
python build\make_pwa.py || goto :err

echo.
echo === XONG. Thu muc "pwa" da san sang de deploy. ===
goto :eof

:err
echo.
echo *** BUILD LOI ***
exit /b 1
