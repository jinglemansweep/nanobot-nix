#!/usr/bin/env bash
set -euo pipefail

# Step 1: Source Nix profile
if [ -f /root/.nix-profile/etc/profile.d/nix.sh ]; then
  . /root/.nix-profile/etc/profile.d/nix.sh
fi

# Step 2: Nanobot onboard (first boot only)
if [ ! -d ~/.nanobot/workspace/ ]; then
  nanobot onboard
fi

# Step 3: Config generation
python3 -m scripts.config_generate

# Step 4: Inject skills
mkdir -p ~/.nanobot/workspace/skills/

# Symlink built-in skills
for dir in /opt/nanobot-nix/skills/*/; do
  ln -sfn "$dir" ~/.nanobot/workspace/skills/"$(basename "$dir")"
done

# Overlay custom skills (custom overrides built-in of same name)
if [ -d /mnt/skills ]; then
  for dir in /mnt/skills/*/; do
    ln -sfn "$dir" ~/.nanobot/workspace/skills/"$(basename "$dir")"
  done
fi

# Step 5: Exec nanobot
exec nanobot "$@"
