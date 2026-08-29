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

PORT=8501

.venv/bin/python -m wonderfeed.netinfo

# Open the browser once the server is up, without blocking the server itself.
# Kept as a detached subshell so there is nothing to poll, wait on, or clean up.
(
  for _ in $(seq 1 60); do
    if curl -s -o /dev/null "http://localhost:$PORT" 2>/dev/null; then
      command -v open >/dev/null 2>&1 && open "http://localhost:$PORT" 2>/dev/null && exit 0
      command -v xdg-open >/dev/null 2>&1 && xdg-open "http://localhost:$PORT" 2>/dev/null && exit 0
      exit 0
    fi
    sleep 1
  done
) >/dev/null 2>&1 &

# Foreground, so closing this window closes the app - as the instructions say.
exec .venv/bin/streamlit run wonderfeed/app.py \
  --server.address 0.0.0.0 \
  --server.port $PORT \
  --server.headless true \
  --browser.gatherUsageStats false \
  --logger.level error
