#!/usr/bin/env bash
# Dung lai toan bo app: du lieu -> ban claude.ai -> ban PWA deploy duoc
set -e
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
PY=${PYTHON:-python3}

echo; echo "[1/4] Ghep anh thanh sprite..."
"$PY" build/sprites.py

echo; echo "[2/4] Dung du lieu va nhung vao HTML..."
"$PY" build/build.py

echo; echo "[3/4] Tao icon..."
"$PY" build/make_icons.py

echo; echo "[4/4] Dung ban PWA (thu muc pwa/)..."
"$PY" build/make_pwa.py

echo; echo '=== XONG. Thu muc "pwa" da san sang de deploy. ==='
