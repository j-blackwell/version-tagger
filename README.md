# version-tagger
Bump, commit, tag and push.

1. Increments your version number from version control tags
2. Writes new version number to `pyproject.toml` `[project.version]` & `uv.lock`
and appends previous commit (so that the current commit is the one with the tag
and the project files all match).
3. Creates a new tag with new version number
4. Pushes changes to the repository.

## Install

```bash
uvx --from version-tagger bump
```
