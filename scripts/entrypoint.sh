#!/usr/bin/env bash
set -euo pipefail

# Step 1: Source Nix profile
if [ -f /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh ]; then
  # shellcheck source=/dev/null
  . /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
fi

# Step 2: Nanobot onboard (first boot only)
if [ ! -d ~/.nanobot/workspace/ ]; then
  nanobot onboard
fi

# Step 3: Docker secrets → env vars
if [ -d /run/secrets ]; then
  for secret in /run/secrets/NANOBOT_*; do
    [ -f "$secret" ] || continue
    name="$(basename "$secret")"
    if [ -z "${!name:-}" ]; then
      export "$name"="$(tr -d '\n' < "$secret")"
    fi
  done
fi

# Step 4: Inject skills
# shellcheck disable=SC1091
source /opt/nanobot-nix/scripts/link-skills.sh
link_skills /opt/nanobot-nix/skills /mnt/skills ~/.nanobot/workspace/skills

# Step 5: Exec nanobot
exec nanobot "$@"
