from pathlib import Path
import git

import toml

from version_tagger import bump


def test_bump_patch(repo: git.Repo, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    manual_version = "1.0.1"

    bump(major=False, minor=False, patch=False, manual=manual_version)

    toml_path = Path(Path(repo.git_dir).parent, "pyproject.toml")
    with open(toml_path, "r") as f:
        data = toml.load(f)

    assert data["project"]["version"] == manual_version
    assert repo.tags[-1].name == f"v{manual_version}"
