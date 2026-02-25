#!/usr/bin/env bash
set -euo pipefail

# Argument validation
if [ $# -ne 1 ]; then
    echo "Usage: nix-search.sh <query>" >&2
    exit 1
fi

query="$1"

# Search execution — try `nix search` first, fall back to `nix-env` for older Nix
if command -v nix &>/dev/null && nix search nixpkgs "$query" 2>/dev/null; then
    :
else
    nix-env -qaP "*${query}*"
fi
