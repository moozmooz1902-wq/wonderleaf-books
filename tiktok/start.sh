#!/usr/bin/env bash
# Wonderfeed. Mac: double-click "Start Wonderfeed.command".
set -e
cd "$(dirname "$0")"

PY=python3
command -v $PY >/dev/null 2>&1 || PY=python
if ! command -v $PY >/dev/null 2>&1; then
  echo
  echo "  Python is not installed."
  echo "  Install it from https://www.python.org/downloads/ and run this again."
  echo
  read -r -p "  Press Enter to close." _
  exit 1
fi

if [ ! -d .venv ]; then
  echo
  echo "  First run - setting up. This takes 2-3 minutes."
  echo
  $PY -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.txt
fi

for f in config/settings.yaml config/products.yaml; do
  [ -f "$f" ] || cp "${f%.yaml}.example.yaml" "$f"
done

.venv/bin/python -m wonderfeed.netinfo

# 0.0.0.0 so other devices on the same wifi can open it too.
exec .venv/bin/streamlit run wonderfeed/app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false
