#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:-jenkins-cicd-demo}"
TIMEOUT="${2:-120}"
EXPECTED="${3:-3}"
end=$((SECONDS + TIMEOUT))

while (( SECONDS < end )); do
  replicas="$(docker service ls --filter "name=${SERVICE}" --format '{{.Replicas}}' | head -n1 || true)"
  state="$(docker service inspect "${SERVICE}" --format '{{if .UpdateStatus}}{{.UpdateStatus.State}}{{else}}none{{end}}' 2>/dev/null || true)"
  echo "service=${SERVICE} replicas=${replicas:-unknown} update=${state:-unknown}"

  if [[ "$replicas" == "${EXPECTED}/${EXPECTED}" ]] && [[ "$state" != "updating" && "$state" != "rollback_started" ]]; then
    exit 0
  fi
  sleep 4
done

echo "Timed out waiting for ${SERVICE}."
docker service ps "${SERVICE}" --no-trunc || true
exit 1
