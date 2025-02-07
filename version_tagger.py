import git
from dunamai import Version
import toml
import typer


def _check_clean_git():
    repo = git.Repo(".")
    if repo.is_dirty(untracked_files=True):
        changes = repo.untracked_files + [x.a_path for x in repo.index.diff(None)]
        print(f"Following files have changes {changes}")
        print("Ensure git tree is clean")
        SystemExit("Exiting...")


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
        return f"{v_list[0]}.{v_list[1]}.{v_list[2]}"
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
    try:
        repo.index.add(["pyproject.toml"])
        repo.git.commit("--amend", "-m", new_message)
        repo.create_tag(f"v{v_new}")
        origin = repo.remote()
        origin.push(force_with_lease=True)
        origin.push(tags=True)
        print(f"Successfully tagged and pushed version {v_new}.")
    except git.GitCommandError as e:
        print(f"Error running git command: {e}")
        SystemExit("Exiting...")


app = typer.Typer()


@app.command()
def bump(
    major: bool = typer.Option(False, "--major", help="Bump the major version"),
    minor: bool = typer.Option(False, "--minor", help="Bump the minor version"),
    patch: bool = typer.Option(False, "--patch", help="Bump the patch version"),
    manual: str = typer.Argument("", help="Set the version explicitly"),
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
    _update_pyproject_toml(v_new)
    _git_commit_and_tag(v_new)


if __name__ == "__main__":
    app()
