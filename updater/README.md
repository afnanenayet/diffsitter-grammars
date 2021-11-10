# updater

## Summary

This is an updater script that will handle updating all of the forked
repositories. It will pull from upstream, remove any Rust bindings/related
code, and handle it recursively for all submodules.

## Usage

This project uses `poetry` for dependency management, so all commands need to
be run through poetry.

To use this:

```sh
poetry run python updater.py "${path_to_submodules}"
```

## Development

Linting and formatting checks are handled with `nox`. Simply run `nox` or
`nox -r` to run the checks.
