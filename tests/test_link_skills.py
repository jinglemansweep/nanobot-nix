import os
import subprocess


SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "link-skills.sh"
)


def run_link_skills(builtin_dir, custom_dir, target_dir):
    """Run link_skills via bash, returning CompletedProcess."""
    return subprocess.run(
        [
            "bash",
            "-c",
            f'source "{SCRIPT_PATH}" && link_skills "$1" "$2" "$3"',
            "_",
            str(builtin_dir),
            str(custom_dir),
            str(target_dir),
        ],
        capture_output=True,
        text=True,
    )


def test_link_builtin_skills(tmp_path):
    """Builtin skills are symlinked into the target directory."""
    builtin = tmp_path / "builtin"
    custom = tmp_path / "custom"
    target = tmp_path / "target"

    (builtin / "skill_a").mkdir(parents=True)
    (builtin / "skill_b").mkdir(parents=True)
    custom.mkdir()
    target.mkdir()

    result = run_link_skills(builtin, custom, target)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    assert (target / "skill_a").is_symlink()
    assert (target / "skill_b").is_symlink()
    assert (target / "skill_a").resolve() == (builtin / "skill_a").resolve()
    assert (target / "skill_b").resolve() == (builtin / "skill_b").resolve()
    # No '*' entry should exist
    assert not (target / "*").exists()


def test_link_custom_skills_override(tmp_path):
    """Custom skills override builtin skills of the same name."""
    builtin = tmp_path / "builtin"
    custom = tmp_path / "custom"
    target = tmp_path / "target"

    (builtin / "skill_a").mkdir(parents=True)
    (custom / "skill_a").mkdir(parents=True)
    target.mkdir()

    result = run_link_skills(builtin, custom, target)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    assert (target / "skill_a").is_symlink()
    assert (target / "skill_a").resolve() == (custom / "skill_a").resolve()


def test_link_custom_skills_merged(tmp_path):
    """Custom and builtin skills are merged into target."""
    builtin = tmp_path / "builtin"
    custom = tmp_path / "custom"
    target = tmp_path / "target"

    (builtin / "skill_a").mkdir(parents=True)
    (custom / "skill_b").mkdir(parents=True)
    target.mkdir()

    result = run_link_skills(builtin, custom, target)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    assert (target / "skill_a").is_symlink()
    assert (target / "skill_a").resolve() == (builtin / "skill_a").resolve()
    assert (target / "skill_b").is_symlink()
    assert (target / "skill_b").resolve() == (custom / "skill_b").resolve()


def test_link_no_skills_no_star_directory(tmp_path):
    """Empty builtin and custom dirs result in empty target (no '*' entry)."""
    builtin = tmp_path / "builtin"
    custom = tmp_path / "custom"
    target = tmp_path / "target"

    builtin.mkdir()
    custom.mkdir()
    target.mkdir()

    result = run_link_skills(builtin, custom, target)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    entries = list(target.iterdir())
    assert entries == [], f"Expected empty target, got: {entries}"


def test_link_no_custom_dir(tmp_path):
    """Nonexistent custom dir is handled without error."""
    builtin = tmp_path / "builtin"
    custom = tmp_path / "nonexistent"
    target = tmp_path / "target"

    (builtin / "skill_a").mkdir(parents=True)
    target.mkdir()

    result = run_link_skills(builtin, custom, target)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    assert (target / "skill_a").is_symlink()
    assert (target / "skill_a").resolve() == (builtin / "skill_a").resolve()


def test_link_target_dir_created(tmp_path):
    """Target directory is created if it doesn't exist."""
    builtin = tmp_path / "builtin"
    custom = tmp_path / "custom"
    target = tmp_path / "target" / "nested"

    (builtin / "skill_a").mkdir(parents=True)
    custom.mkdir()

    assert not target.exists()

    result = run_link_skills(builtin, custom, target)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    assert target.is_dir()
    assert (target / "skill_a").is_symlink()
    assert (target / "skill_a").resolve() == (builtin / "skill_a").resolve()
