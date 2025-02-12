import git

from version_tagger import _git_commit_and_tag


def test_git_commit_and_tag(repo: git.Repo, monkeypatch):
    new_version = "2.0.0"

    monkeypatch.setattr("builtins.input", lambda _: "y")

    _git_commit_and_tag(repo, new_version)

    assert repo.tags[-1].name == f"v{new_version}"
    assert "version(2.0.0)" in str(repo.head.commit.message)
