#!/usr/bin/env bash
set -euo pipefail

port="${1:-9000}"
[[ "$port" =~ ^[0-9]{1,5}$ ]] && ((10#$port > 0 && 10#$port <= 65535)) || exit 1

# The management endpoint is always loopback HTTP; no general-purpose HTTP/TLS
# client is needed. Bound the entire exchange, including connection setup.
timeout 3 bash -s -- "$port" <<'BASH'
    set -euo pipefail
    exec 3<>/dev/tcp/127.0.0.1/"$1"
    printf "GET /health/ready HTTP/1.0\r\nHost: localhost\r\nConnection: close\r\n\r\n" >&3
    IFS= read -r -t 2 status <&3
    [[ "$status" =~ ^HTTP/1\.[01]\ 200\  ]]
BASH
