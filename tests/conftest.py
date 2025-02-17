import os
import pytest
from pathlib import Path
import shutil
import git
import toml
import uuid


@pytest.fixture(scope="module")
def repo():
    original_wd = os.getcwd()
    repo_id = str(uuid.uuid4()).split("-")[0]
    repo_path = Path(".local", repo_id).resolve()
    if repo_path.exists():
        shutil.rmtree(repo_path)
    repo_path.mkdir(parents=True, exist_ok=True)

    print(f"\nCreating test repo at: {repo_path.relative_to(original_wd)}\n")
    repo = git.Repo.init(repo_path)
    repo.git.config("user.name", "github-actions")
    repo.git.config("user.email", "github-actions@github.com")
    os.chdir(repo_path)

    pyproject_path = Path(repo_path, "pyproject.toml")
    pyproject_data = {"project": {"name": "testing", "version": "1.0.0"}}
    with open(pyproject_path, "w") as f:
        toml.dump(pyproject_data, f)

    repo.index.add([str(pyproject_path)])
    repo.index.commit("Initial commit with pyproject.toml")
    # repo.create_tag("v1.0.0")

    yield repo

    os.chdir(original_wd)
    print(f"\nRemoving test repo at: {repo_path.relative_to(original_wd)}\n")
    shutil.rmtree(repo_path)
