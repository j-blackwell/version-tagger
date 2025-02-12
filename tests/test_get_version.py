import git
from dunamai import Version

from version_tagger import _get_current_version, _update_version


def test_get_version_empty(repo: git.Repo):
    version = _get_current_version(repo)
    assert version.base == "0.0.0"

    version_new = _update_version(
        version,
        major=False,
        minor=False,
        patch=True,
        manual="",
    )

    assert version_new == "0.0.1"


def test_get_version_non_empty(repo: git.Repo):
    repo.create_tag("v0.0.1")
    version = _get_current_version(repo)
    assert version.base == "0.0.1"

    version_new = _update_version(
        version,
        major=False,
        minor=False,
        patch=True,
        manual="",
    )

    assert version_new == "0.0.2"
