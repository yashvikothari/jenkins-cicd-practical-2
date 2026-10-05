#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:-jenkins-cicd-demo}"
TIMEOUT="${2:-60}"
end=$((SECONDS + TIMEOUT))

while (( SECONDS < end )); do
  state="$(docker service inspect "${SERVICE}" --format '{{if .UpdateStatus}}{{.UpdateStatus.State}}{{else}}none{{end}}' 2>/dev/null || true)"
  message="$(docker service inspect "${SERVICE}" --format '{{if .UpdateStatus}}{{.UpdateStatus.Message}}{{end}}' 2>/dev/null || true)"
  echo "update_state=${state:-unknown} message=${message:-none}"
  if [[ "$state" == "paused" ]]; then
    exit 0
  fi
  sleep 3
done

echo "Controlled update did not reach paused state."
docker service ps "${SERVICE}" --no-trunc || true
exit 1
