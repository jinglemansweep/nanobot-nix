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
