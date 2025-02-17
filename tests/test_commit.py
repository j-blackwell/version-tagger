import git
from pathlib import Path

from version_tagger import _git_commit_and_tag


def test_git_commit_and_tag(repo: git.Repo, monkeypatch):
    new_version = "2.0.0"

    monkeypatch.setattr("builtins.input", lambda _: "y")

    Path(repo.working_dir, "uv.lock").touch()
    _git_commit_and_tag(repo, new_version, append=False)
    assert repo.tags[-1].name == f"v{new_version}"
    assert f"version({new_version})\n" == str(repo.head.commit.message)

    new_version = "2.0.1"
    _git_commit_and_tag(repo, new_version, append=True)
    assert repo.tags[-1].name == f"v{new_version}"
    assert f"version({new_version})" in str(repo.head.commit.message)
