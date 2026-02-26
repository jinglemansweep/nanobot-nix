#!/usr/bin/env bash
set -euo pipefail

check_package_allowed() {
  local pkg="$1"

  if [ -z "${NANOBOT_NIX_ALLOWED_PACKAGES:-}" ]; then
    echo "Nix package installation is disabled (NANOBOT_NIX_ALLOWED_PACKAGES is not set)" >&2
    return 1
  fi

  if [ "$NANOBOT_NIX_ALLOWED_PACKAGES" = "*" ]; then
    return 0
  fi

  IFS=',' read -ra entries <<< "$NANOBOT_NIX_ALLOWED_PACKAGES"
  for entry in "${entries[@]}"; do
    trimmed="${entry#"${entry%%[![:space:]]*}"}"
    trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
    if [ "$trimmed" = "$pkg" ]; then
      return 0
    fi
  done

  echo "Package '$pkg' is not in the allowed list" >&2
  return 1
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  # Argument validation
  if [ $# -ne 1 ]; then
    echo "Usage: nix-install.sh <package>" >&2
    exit 1
  fi

  package="$1"

  # Whitelist check
  check_package_allowed "$package" || exit 1

  # Already-installed check
  if nix profile list 2>/dev/null | grep -q "nixpkgs#$package"; then
    echo "Package '$package' is already installed"
    exit 0
  fi

  # Installation
  if ! nix profile install "nixpkgs#$package"; then
    echo "Failed to install package '$package'" >&2
    exit 1
  fi

  echo "Package '$package' installed successfully"
fi
