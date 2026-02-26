import os
import subprocess


SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "nix-install.sh"
)


def run_check_package_allowed(package, env_vars=None):
    """Run check_package_allowed via bash, returning CompletedProcess."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
    if env_vars:
        env.update(env_vars)
    return subprocess.run(
        [
            "bash",
            "-c",
            f'source "{SCRIPT_PATH}" && check_package_allowed "$1"',
            "_",
            package,
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def test_allowed_packages_wildcard_env_chain():
    """Verify NANOBOT_NIX_ALLOWED_PACKAGES='*' survives env chain without shell expansion."""
    result = run_check_package_allowed(
        "curl",
        env_vars={"NANOBOT_NIX_ALLOWED_PACKAGES": "*"},
    )
    assert result.returncode == 0, (
        f"Expected return code 0 (allow), got {result.returncode}. "
        f"stderr: {result.stderr}"
    )


def test_allowed_packages_unset():
    """When NANOBOT_NIX_ALLOWED_PACKAGES is not set, installation is disabled."""
    result = run_check_package_allowed("curl")
    assert result.returncode == 1
    assert "disabled" in result.stderr


def test_allowed_packages_empty_string():
    """When NANOBOT_NIX_ALLOWED_PACKAGES is empty, installation is disabled."""
    result = run_check_package_allowed(
        "curl",
        env_vars={"NANOBOT_NIX_ALLOWED_PACKAGES": ""},
    )
    assert result.returncode == 1
    assert "disabled" in result.stderr


def test_allowed_packages_wildcard():
    """When NANOBOT_NIX_ALLOWED_PACKAGES='*', all packages are allowed."""
    result = run_check_package_allowed(
        "curl",
        env_vars={"NANOBOT_NIX_ALLOWED_PACKAGES": "*"},
    )
    assert result.returncode == 0


def test_allowed_packages_exact_match():
    """A package in the comma-separated list is allowed."""
    result = run_check_package_allowed(
        "wget",
        env_vars={"NANOBOT_NIX_ALLOWED_PACKAGES": "curl,wget,jq"},
    )
    assert result.returncode == 0


def test_allowed_packages_no_match():
    """A package not in the list is rejected."""
    result = run_check_package_allowed(
        "vim",
        env_vars={"NANOBOT_NIX_ALLOWED_PACKAGES": "curl,wget,jq"},
    )
    assert result.returncode == 1
    assert "not in the allowed list" in result.stderr


def test_allowed_packages_whitespace_trimming():
    """Whitespace around entries in the list is trimmed."""
    result = run_check_package_allowed(
        "wget",
        env_vars={"NANOBOT_NIX_ALLOWED_PACKAGES": "curl , wget , jq"},
    )
    assert result.returncode == 0


def test_allowed_packages_single_entry():
    """A single entry (no commas) works correctly."""
    result = run_check_package_allowed(
        "curl",
        env_vars={"NANOBOT_NIX_ALLOWED_PACKAGES": "curl"},
    )
    assert result.returncode == 0


def test_allowed_packages_trailing_comma():
    """A trailing comma in the list does not cause errors."""
    result = run_check_package_allowed(
        "wget",
        env_vars={"NANOBOT_NIX_ALLOWED_PACKAGES": "curl,wget,"},
    )
    assert result.returncode == 0
