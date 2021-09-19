# diffsitter grammars

## Synopsis

This is a repository to keep track of diffsitter dependencies in forked
repositories.

For diffsitter we have forked the grammars so that we can use our own
`build.rs` script and statically link grammars.

## Dependencies

You'll need: `git` and `nvchecker`.

You'll need the forked repositories. We use `nvchecker` to keep track of when
we're out of date with master.

Checking for repositories that are out of date:

```sh
nvchecker -c nvchecker.toml
```

You can also use the `Makefile`:

```sh
make check
```

Updating the nvchecker version file once you have updated a repository:

```sh
# substitute for any repository name
LANGUAGE="c-sharp"
nvtake -c nvchecker.toml "tree-sitter-${LANGUAGE}"
```

If you have updated the repository for the grammar then you should open a PR
here to reflect that.

It is recommended that you create a `keyfile.toml` with API tokens for Github,
otherwise you will get rate limited very quickly because of all of the
requests that `nvchecker` invokes.

Example `keyfile.toml`:

```toml
[keys]
github = "ghp_REDACTED"
```
