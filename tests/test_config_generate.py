import json
import os

from scripts.config_generate import (
    generate,
    infer_type,
    read_docker_secrets,
    resolve_aliases,
    set_nested,
)


def test_infer_type_bool_true():
    assert infer_type("SOME_FIELD", "true") is True


def test_infer_type_bool_false():
    assert infer_type("SOME_FIELD", "false") is False


def test_infer_type_int():
    result = infer_type("SOME_FIELD", "42")
    assert result == 42
    assert isinstance(result, int)


def test_infer_type_float():
    result = infer_type("SOME_FIELD", "3.14")
    assert result == 3.14
    assert isinstance(result, float)


def test_infer_type_json_object():
    assert infer_type("SOME_FIELD", '{"key": "val"}') == {"key": "val"}


def test_infer_type_json_array():
    assert infer_type("SOME_FIELD", '[1, 2]') == [1, 2]


def test_infer_type_csv_array_field():
    result = infer_type("CHANNELS_TELEGRAM_ALLOWFROM", "alice, bob, charlie")
    assert result == ["alice", "bob", "charlie"]


def test_infer_type_csv_non_array_field():
    result = infer_type("SOME_FIELD", "a, b, c")
    assert result == "a, b, c"


def test_infer_type_single_numeric_array_field():
    result = infer_type("CHANNELS_DISCORD_ALLOWFROM", "701044353249837097")
    assert result == ["701044353249837097"]
    assert isinstance(result, list)


def test_infer_type_single_string_array_field():
    result = infer_type("CHANNELS_TELEGRAM_ALLOWFROM", "alice")
    assert result == ["alice"]
    assert isinstance(result, list)


def test_infer_type_csv_numeric_array_field():
    result = infer_type("CHANNELS_DISCORD_ALLOWFROM", "123456789,987654321")
    assert result == ["123456789", "987654321"]


def test_infer_type_plain_string():
    assert infer_type("SOME_FIELD", "hello") == "hello"


def test_set_nested_creates_path():
    config = {}
    set_nested(config, ("a", "b", "c"), "val")
    assert config == {"a": {"b": {"c": "val"}}}


def test_set_nested_overwrites():
    config = {"a": {"b": "old"}}
    set_nested(config, ("a", "b"), "new")
    assert config == {"a": {"b": "new"}}


def test_resolve_aliases(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("NANOBOT_PROVIDERS_OPENROUTER_APIKEY", raising=False)
    resolve_aliases()
    assert os.environ["NANOBOT_PROVIDERS_OPENROUTER_APIKEY"] == "test-key"


def test_resolve_zhipu_alias(monkeypatch):
    monkeypatch.setenv("ZHIPU_API_KEY", "alias-zhipu-key")
    monkeypatch.delenv("NANOBOT_PROVIDERS_ZHIPU_APIKEY", raising=False)
    resolve_aliases()
    assert os.environ["NANOBOT_PROVIDERS_ZHIPU_APIKEY"] == "alias-zhipu-key"


def test_resolve_aliases_does_not_overwrite(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "alias-val")
    monkeypatch.setenv("NANOBOT_PROVIDERS_OPENROUTER_APIKEY", "canonical-val")
    resolve_aliases()
    assert os.environ["NANOBOT_PROVIDERS_OPENROUTER_APIKEY"] == "canonical-val"


def test_read_docker_secrets(monkeypatch, tmp_path):
    secret_file = tmp_path / "NANOBOT_TEST_SECRET"
    secret_file.write_text("secret-value\n")

    monkeypatch.delenv("NANOBOT_TEST_SECRET", raising=False)
    monkeypatch.setattr(
        "scripts.config_generate.read_docker_secrets.__code__",
        read_docker_secrets.__code__,
    )

    # Patch the secrets_dir inside the function by patching os functions
    real_isdir = os.path.isdir
    real_listdir = os.listdir
    real_join = os.path.join
    real_isfile = os.path.isfile

    def fake_isdir(path):
        if path == "/run/secrets":
            return True
        return real_isdir(path)

    def fake_listdir(path):
        if path == "/run/secrets":
            return ["NANOBOT_TEST_SECRET"]
        return real_listdir(path)

    def fake_join(base, *parts):
        if base == "/run/secrets":
            return real_join(str(tmp_path), *parts)
        return real_join(base, *parts)

    def fake_isfile(path):
        if str(tmp_path) in str(path):
            return real_isfile(path)
        return real_isfile(path)

    monkeypatch.setattr("os.path.isdir", fake_isdir)
    monkeypatch.setattr("os.listdir", fake_listdir)
    monkeypatch.setattr("os.path.join", fake_join)
    monkeypatch.setattr("os.path.isfile", fake_isfile)

    read_docker_secrets()
    assert os.environ.get("NANOBOT_TEST_SECRET") == "secret-value"


def test_generate_full_pipeline(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("NANOBOT_PROVIDERS_OPENROUTER_APIKEY", "test-key-123")

    # Remove any other NANOBOT_ env vars that might interfere
    for key in list(os.environ.keys()):
        if key.startswith("NANOBOT_") and key != "NANOBOT_PROVIDERS_OPENROUTER_APIKEY":
            monkeypatch.delenv(key, raising=False)

    # Patch read_docker_secrets to be a no-op (no /run/secrets in test env)
    monkeypatch.setattr("scripts.config_generate.read_docker_secrets", lambda: None)

    nanobot_dir = tmp_path / ".nanobot"
    nanobot_dir.mkdir()

    generate()

    config_path = nanobot_dir / "config.json"
    assert config_path.exists()

    config = json.loads(config_path.read_text())
    assert config["providers"]["openrouter"]["apiKey"] == "test-key-123"
    assert config["agents"]["defaults"]["model"] == "anthropic/claude-sonnet-4-5-20250514"


def test_generate_zhipu_provider(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("NANOBOT_PROVIDERS_ZHIPU_APIKEY", "zhipu-test-key-456")
    monkeypatch.setenv(
        "NANOBOT_PROVIDERS_ZHIPU_APIBASE",
        "https://api.z.ai/api/coding/paas/v4",
    )

    for key in list(os.environ.keys()):
        if key.startswith("NANOBOT_") and key not in (
            "NANOBOT_PROVIDERS_ZHIPU_APIKEY",
            "NANOBOT_PROVIDERS_ZHIPU_APIBASE",
        ):
            monkeypatch.delenv(key, raising=False)

    monkeypatch.setattr("scripts.config_generate.read_docker_secrets", lambda: None)

    nanobot_dir = tmp_path / ".nanobot"
    nanobot_dir.mkdir()

    generate()

    config_path = nanobot_dir / "config.json"
    config = json.loads(config_path.read_text())
    assert config["providers"]["zhipu"]["apiKey"] == "zhipu-test-key-456"
    assert (
        config["providers"]["zhipu"]["apiBase"]
        == "https://api.z.ai/api/coding/paas/v4"
    )
    assert config["agents"]["defaults"]["model"] == "anthropic/claude-sonnet-4-5-20250514"
