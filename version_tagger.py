from pathlib import Path
import git
from dunamai import Version
import toml
import typer
from typer.main import subprocess


def _check_clean_git():
    repo = git.Repo(".")
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
    new_message = f"{current_message}\n\nvesion({v_new})"
    additions = ["pyproject.toml"]

    if Path("uv.lock").exists():
        subprocess.run(["uv", "sync"])
        additions.append("uv.lock")

    repo.index.add(additions)
    repo.git.commit("--amend", "-m", new_message)
    repo.create_tag(f"v{v_new}")
    origin = repo.remote()
    origin.push(force_with_lease=True)
    origin.push(tags=True)


app = typer.Typer()


@app.command()
def bump(
    major: bool = False,
    minor: bool = False,
    patch: bool = False,
    manual: str = "",
    dry_run: bool = False,
):
    flags = {"major": major, "minor": minor, "patch": patch, "manual": manual}
    flags_set = [k for k, v in flags.items() if v]
    if len(flags_set) > 1:
        raise ValueError(f"Cannot have more than one flag set {flags_set}.")
    elif len(flags_set) == 0:
        raise ValueError(f"Must have one flag set.")

    _check_clean_git()
    v = Version.from_git()
    v_new = _update_version(v, major, minor, patch, manual)

    print(f"Updating {v.base} -> {v_new}")
    if dry_run:
        print("Dry run, not updating...")
        return

    _update_pyproject_toml(v_new)
    _git_commit_and_tag(v_new)


if __name__ == "__main__":
    app()
