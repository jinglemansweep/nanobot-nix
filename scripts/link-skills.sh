#!/usr/bin/env bash
set -euo pipefail

link_skills() {
  local builtin_skills_dir="$1"
  local custom_skills_dir="$2"
  local target_dir="$3"

  mkdir -p "$target_dir"

  shopt -s nullglob

  # Symlink built-in skills
  for dir in "$builtin_skills_dir"/*/; do
    ln -sfn "$dir" "$target_dir/$(basename "$dir")"
  done

  # Overlay custom skills (custom overrides built-in of same name)
  if [ -d "$custom_skills_dir" ]; then
    for dir in "$custom_skills_dir"/*/; do
      ln -sfn "$dir" "$target_dir/$(basename "$dir")"
    done
  fi

  shopt -u nullglob
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  link_skills "$@"
fi
