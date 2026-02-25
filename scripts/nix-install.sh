#!/usr/bin/env bash
set -euo pipefail

# Argument validation
if [ $# -ne 1 ]; then
    echo "Usage: nix-install.sh <package>" >&2
    exit 1
fi

package="$1"

# Whitelist check
if [ -z "${NANOBOT_NIX_ALLOWED_PACKAGES:-}" ]; then
    echo "Nix package installation is disabled (NANOBOT_NIX_ALLOWED_PACKAGES is not set)" >&2
    exit 1
fi

if [ "$NANOBOT_NIX_ALLOWED_PACKAGES" != "*" ]; then
    allowed=false
    IFS=',' read -ra entries <<< "$NANOBOT_NIX_ALLOWED_PACKAGES"
    for entry in "${entries[@]}"; do
        trimmed="${entry#"${entry%%[![:space:]]*}"}"
        trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
        if [ "$trimmed" = "$package" ]; then
            allowed=true
            break
        fi
    done
    if [ "$allowed" = false ]; then
        echo "Package '$package' is not in the allowed list" >&2
        exit 1
    fi
fi

# Already-installed check
if nix-env -qaP "nixpkgs.$package" --installed 2>/dev/null | grep -q .; then
    echo "Package '$package' is already installed"
    exit 0
fi

# Installation
if ! nix-env -iA "nixpkgs.$package"; then
    echo "Failed to install package '$package'" >&2
    exit 1
fi

echo "Package '$package' installed successfully"
