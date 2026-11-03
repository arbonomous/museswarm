#!/bin/zsh
# No install, pull, permission change or automatic API request.
cd "$(dirname "$0")"
if [[ "$(uname -s)" != Darwin ]]; then echo 'Mac required. Nothing started.'; exit 1; fi
PY="$PWD/.venv/bin/python"
if ! "$PY" -c 'import AppKit, dotenv, openai' 2>/dev/null; then
  PY=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
  if ! "$PY" -c 'import AppKit, dotenv, openai' 2>/dev/null; then
    echo 'Existing Mac Python lacks AppKit/model dependencies. Nothing installed or started.'; exit 1
  fi
fi
exec "$PY" staged_product_mac.py
