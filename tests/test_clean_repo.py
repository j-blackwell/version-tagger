import git
import pytest
import typer
from pathlib import Path

from version_tagger import _check_clean_git


def test_check_clean_git_clean(repo: git.Repo):
    assert not repo.is_dirty()
    _check_clean_git(repo)


def test_check_clean_git_dirty(repo: git.Repo):
    new_file = Path(Path(repo.git_dir).parent, "new_file.txt")
    new_file.touch()
    repo.index.add([str(new_file)])
    with pytest.raises(typer.Exit):
        _check_clean_git(repo)
