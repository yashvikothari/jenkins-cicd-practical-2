#!/usr/bin/env bash
set -euo pipefail

URL="${1:-http://127.0.0.1:8090/health}"
TIMEOUT="${2:-60}"
end=$((SECONDS + TIMEOUT))

while (( SECONDS < end )); do
  if body="$(curl -fsS "$URL" 2>/dev/null)"; then
    echo "Application verification succeeded:"
    echo "$body"
    exit 0
  fi
  echo "Waiting for application at $URL ..."
  sleep 3
done

echo "Application verification failed: $URL"
exit 1
