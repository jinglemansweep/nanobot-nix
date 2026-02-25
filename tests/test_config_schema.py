from scripts.config_schema import ALIASES, ARRAY_FIELDS, DEFAULTS, ENV_MAP


def test_env_map_values_are_tuples():
    for key, value in ENV_MAP.items():
        assert isinstance(value, tuple), f"ENV_MAP[{key!r}] is not a tuple"
        assert len(value) >= 1, f"ENV_MAP[{key!r}] is empty"


def test_env_map_values_contain_strings():
    for key, value in ENV_MAP.items():
        for i, element in enumerate(value):
            assert isinstance(element, str), (
                f"ENV_MAP[{key!r}][{i}] is not a str"
            )


def test_array_fields_exist_in_env_map():
    for field in ARRAY_FIELDS:
        assert field in ENV_MAP, f"ARRAY_FIELDS entry {field!r} not in ENV_MAP"


def test_aliases_point_to_valid_canonical_names():
    for alias, canonical in ALIASES.items():
        assert canonical.startswith("NANOBOT_"), (
            f"ALIASES[{alias!r}] value {canonical!r} does not start with NANOBOT_"
        )
        suffix = canonical[len("NANOBOT_"):]
        assert suffix in ENV_MAP, (
            f"ALIASES[{alias!r}] suffix {suffix!r} not found in ENV_MAP"
        )


def test_defaults_is_dict():
    assert isinstance(DEFAULTS, dict)


def test_no_duplicate_env_map_paths():
    seen = {}
    for key, path in ENV_MAP.items():
        assert path not in seen, (
            f"Duplicate path {path!r}: ENV_MAP[{key!r}] and ENV_MAP[{seen[path]!r}]"
        )
        seen[path] = key
