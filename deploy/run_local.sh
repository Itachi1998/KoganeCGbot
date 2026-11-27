#!/usr/bin/env bash
# Start the bot in this terminal. Reads deploy/.env if present (see deploy/LOCAL.md).
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f deploy/.env ]; then set -a; . deploy/.env; set +a; fi
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
export REDIS_REQUIRED="${REDIS_REQUIRED:-1}"
export CULLING_SQLITE="${CULLING_SQLITE:-$HOME/kogane-data/culling.db}"
mkdir -p "$(dirname "$CULLING_SQLITE")"
if ! redis-cli -u "$REDIS_URL" ping >/dev/null 2>&1; then
  echo "Redis is not answering at $REDIS_URL - start it first (sudo systemctl start redis-server)." >&2
  exit 1
fi
PY=".venv/bin/python"; [ -x "$PY" ] || PY=python3
exec "$PY" -m ai.bot
