#!/usr/bin/env bash
set -euo pipefail

log() {
    echo "[INFO] $*"
    }
die() {
    echo "[ERROR] $*" >&2
    exit 1
    }

overall_status=0

log "Starting security gate..."

DOCKERFILES=("catalogue-web/Dockerfile" "inventory-api/Dockerfile")

for dockerfile in "${DOCKERFILES[@]}"; do
    if hadolint "$dockerfile"; then
        log "hadolint ($dockerfile) PASS"
    else
        log "hadolint ($dockerfile) FAIL"
        overall_status=1
    fi
done

if trivy config --severity CRITICAL,HIGH --exit-code 1  .; then
    log "trivy config PASS"
else
    log "trivy config FAIL"
    overall_status=1
fi

if trivy fs --scanners vuln,secret --severity CRITICAL,HIGH --exit-code 1 .; then
    log "trivy fs PASS"
else
    log "trivy fs FAIL"
    overall_status=1
fi

if [ "$overall_status" -eq 0 ]; then
    log "overall PASS"
else
    die "overall FAIL"
fi

