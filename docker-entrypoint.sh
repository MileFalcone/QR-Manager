#!/bin/sh
set -e

# Initialize DB if it doesn't exist (first run)
flask init-db 2>/dev/null || true

exec "$@"
