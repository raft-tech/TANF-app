#!/usr/bin/env bash
set -euo pipefail

check_runtime_security() {
    local status_file="$1" field value seen=0
    while read -r field value; do
        case "$field" in
            Uid:)
                local real effective saved filesystem extra
                read -r real effective saved filesystem extra <<< "$value"
                [[ "$real" =~ ^[1-9][0-9]*$ && "$real" == "$effective" &&
                    "$real" == "$saved" && "$real" == "$filesystem" && -z "$extra" ]] || return 1
                seen=$((seen | 1)) ;;
            CapInh:|CapPrm:|CapEff:|CapAmb:)
                [[ "$value" =~ ^0+$ ]] || return 1
                case "$field" in
                    CapInh:) seen=$((seen | 2)) ;;
                    CapPrm:) seen=$((seen | 4)) ;;
                    CapEff:) seen=$((seen | 8)) ;;
                    CapAmb:) seen=$((seen | 16)) ;;
                esac ;;
        esac
    done < "$status_file"
    [[ "$seen" == 31 ]]
}

require_runtime_security() {
    # ACL pathname operations must never run with privileges over another UID.
    if ! check_runtime_security /proc/self/status; then
        echo 'ERROR: Keycloak requires a non-root UID and no inherited, permitted, effective, or ambient capabilities.' >&2
        exit 1
    fi
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    require_runtime_security
fi
