#!/usr/bin/env bash
# Dung lai toan bo app: du lieu -> ban claude.ai -> ban PWA deploy duoc
set -e
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
PY=${PYTHON:-python3}

if [ ! -f build/fonts/fonts.css ]; then
  echo; echo "[0/5] Tai phong chu ve de tu host..."
  "$PY" build/get_fonts.py
fi

echo; echo "[1/5] Ghep anh thanh sprite..."
"$PY" build/sprites.py

echo; echo "[2/5] Dung du lieu va nhung vao HTML..."
"$PY" build/build.py

echo; echo "[3/5] Tao icon..."
"$PY" build/make_icons.py

echo; echo "[4/5] Dung ban PWA (thu muc pwa/)..."
"$PY" build/make_pwa.py

echo; echo '=== XONG. Thu muc "pwa" da san sang de deploy. ==='
