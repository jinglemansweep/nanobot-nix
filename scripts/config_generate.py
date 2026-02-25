"""Generate ~/.nanobot/config.json from environment variables and Docker secrets."""

import copy
import json
import logging
import os
import sys

from .config_schema import ALIASES, ARRAY_FIELDS, DEFAULTS, ENV_MAP

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr)
log = logging.getLogger(__name__)


def read_docker_secrets():
    """Read Docker secrets from /run/secrets/ and set as env vars (if not already set)."""
    secrets_dir = "/run/secrets"
    if not os.path.isdir(secrets_dir):
        return
    for name in os.listdir(secrets_dir):
        if not name.startswith("NANOBOT_"):
            continue
        if name in os.environ:
            continue
        path = os.path.join(secrets_dir, name)
        if os.path.isfile(path):
            with open(path) as f:
                os.environ[name] = f.read().rstrip()


def resolve_aliases():
    """Resolve alias env vars to their canonical names."""
    resolved = 0
    for alias, canonical in ALIASES.items():
        if alias in os.environ and canonical not in os.environ:
            os.environ[canonical] = os.environ[alias]
            resolved += 1
            log.info("Resolved alias %s -> %s", alias, canonical)
    return resolved


def infer_type(suffix, value):
    """Infer the Python type for a string value."""
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if value.startswith("[") or value.startswith("{"):
        return json.loads(value)

    if suffix in ARRAY_FIELDS and "," in value:
        return [item.strip() for item in value.split(",")]

    return value


def set_nested(config, path, value):
    """Set a value in a nested dict, creating intermediate dicts as needed."""
    current = config
    for key in path[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[path[-1]] = value


def generate():
    """Run the full config generation pipeline."""
    config = copy.deepcopy(DEFAULTS)

    read_docker_secrets()
    aliases_resolved = resolve_aliases()

    processed = 0
    skipped = 0
    for key, value in os.environ.items():
        if not key.startswith("NANOBOT_"):
            continue
        suffix = key[len("NANOBOT_"):]
        if suffix not in ENV_MAP:
            log.warning("Unknown config key: NANOBOT_%s, skipping", suffix)
            skipped += 1
            continue
        path = ENV_MAP[suffix]
        typed_value = infer_type(suffix, value)
        set_nested(config, path, typed_value)
        processed += 1

    output_dir = os.path.expanduser("~/.nanobot")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "config.json")

    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    log.info("Processed %d env var(s), skipped %d unknown key(s), resolved %d alias(es)", processed, skipped, aliases_resolved)
    log.info("Config written to %s", output_path)


if __name__ == "__main__":
    generate()
