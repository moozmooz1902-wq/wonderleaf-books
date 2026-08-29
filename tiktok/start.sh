#!/usr/bin/env bash
# Wonderfeed desktop. Double-click, or run ./start.sh
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "First run - setting up..."
  python3 -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.txt
fi

for f in config/settings.yaml config/products.yaml; do
  [ -f "$f" ] || cp "${f%.yaml}.example.yaml" "$f"
done

echo "Opening Wonderfeed at http://localhost:8501"
exec .venv/bin/streamlit run wonderfeed/app.py
