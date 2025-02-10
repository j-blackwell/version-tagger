from pathlib import Path
from typing import Annotated
import git
from dunamai import Version
import toml
import typer
import subprocess


def _check_clean_git():
    repo = git.Repo(".")

    try:
        origin = repo.remote()
        origin.pull()
    except git.GitCommandError as e:
        raise git.GitCommandError("Divergent branch - resolve before bumping.") from e

    if repo.is_dirty(untracked_files=True):
        changes = repo.untracked_files + [x.a_path for x in repo.index.diff(None)]
        message = f"""Following files have changes {changes}
Ensure git tree is clean before continuing.
Exiting..."""
        raise ValueError(message)


def _update_version(
    v: Version,
    major: bool,
    minor: bool,
    patch: bool,
    manual: str,
) -> str:
    v_list = [int(x) for x in v.base.split(".")]
    if major:
        return f"{v_list[0]+1}.0.0"
    if minor:
        return f"{v_list[0]}.{v_list[1]+1}.0"
    if patch:
        return f"{v_list[0]}.{v_list[1]}.{v_list[2]+1}"
    else:
        return manual


def _update_pyproject_toml(v_new: str):
    with open("pyproject.toml", "r") as f:
        data = toml.load(f)

    data["project"]["version"] = v_new

    with open("pyproject.toml", "w") as f:
        toml.dump(data, f)


def _git_commit_and_tag(v_new: str):
    repo = git.Repo(".")
    current_message = repo.head.commit.message.strip()
    new_message = f"{current_message}\n\nversion({v_new})"
    additions = ["pyproject.toml"]

    if Path("uv.lock").exists():
        subprocess.run(["uv", "sync"])
        additions.append("uv.lock")

    repo.index.add(additions)

    # TODO: Check here
    result = subprocess.run(
        ["git", "diff", "--staged", "--color=always"], capture_output=True, text=True
    )
    print(result.stdout)

    response = input("Proceed with updating pyproject.toml and git? [Y]/n\n")

    if response.lower() in {"y", "yes", ""}:
        repo.git.commit("--amend", "-m", new_message)
        repo.create_tag(f"v{v_new}")
        origin = repo.remote()
        origin.push(force_with_lease=True)
        origin.push(tags=True)
    else:
        repo.git.reset("--hard")
        raise ValueError()


app = typer.Typer()


@app.command()
def bump(
    major: bool = typer.Option(default=False, help="Bump major version"),
    minor: bool = typer.Option(default=False, help="Bump minor version"),
    patch: bool = typer.Option(default=True, help="Bump patch version"),
    manual: str = typer.Argument(
        default="",
        help="Set version manually in {major}.{minor}.{patch} format",
    ),
):
    """
    Bump, commit, tag, push.

    Bump your version number by one patch, minor or major number.
    Or set version number manually.

    Version numbers are assumed to be in the format:\n\n

    `v{major}.{minor}.{patch}`\n\n

    The old version number will be retreived from the version control tag.

    `bump` will then increment the version number, before writing the new value
    to the `pyproject.toml` file and `uv.lock` file (if exists).
    It will commit these changes to the repo (appending to the previous commit),
    tag the commit with the version number, and push the changes.
    """
    flags = {"major": major, "minor": minor, "patch": patch, "manual": manual}
    flags_set = [k for k, v in flags.items() if v]
    if len(flags_set) > 1:
        raise ValueError(f"Cannot have more than one flag set {flags_set}.")
    elif len(flags_set) == 0:
        raise ValueError(f"Must have one flag set.")

    _check_clean_git()
    v = Version.from_any_vcs(latest_tag=True)
    v_new = _update_version(v, major, minor, patch, manual)

    print(f"Updating {v.base} -> {v_new}")
    _update_pyproject_toml(v_new)
    _git_commit_and_tag(v_new)


if __name__ == "__main__":
    app()
