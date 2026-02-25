#!/usr/bin/env bash
set -euo pipefail

# Argument validation
if [ $# -ne 1 ]; then
    echo "Usage: nix-search.sh <query>" >&2
    exit 1
fi

query="$1"

# Search execution
nix search nixpkgs "$query"
