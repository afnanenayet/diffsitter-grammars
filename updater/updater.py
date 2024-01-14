"""A script that recursively updates all repositories in a path.

Given a path, this script will find all of the valid git repositories under it, and then pull the
default branch from upstream, and then delete any Rust bindings in the repository.
"""

from pathlib import Path
from typing import List

import click
from loguru import logger
from plumbum import ProcessExecutionError, local
from rich import traceback


def find_git_repositories(p: Path) -> List[Path]:
    """Find all git repositories in a given path.

    Args:
        p: The path to recursively search.

    Returns:
        A list of git repositories found in the path.
    """
    child_repos = []

    for child_path in p.rglob("*"):
        if child_path.is_dir() and child_path.stem == ".git":
            repo_path = child_path.parent.absolute()
            logger.info(f"Found repo {repo_path}")
            child_repos.append(repo_path)

    return child_repos


def update_grammar_repo(p: Path) -> None:
    """Update the repository for a grammar.

    This will perform the following steps:

    * Clean the repository
    * Check if the upstream is ahead of the origin's default branch
    * Merge without commit
    * Remove any rust binding code
    * Add files and commit the merge
    * Push to origin

    Args:
        p: The path to a repository root for a tree-sitter grammar.
    """
    logger.debug(f"Updating repo {p}")

    with local.cwd(p):
        # Clean the local repository before merging
        git = local["git"]
        rg = local["rg"]
        rm = local["rm"]
        git["clean", "-f", "-d"]()

        # Get the default branch (since people will use "main" or "master" generally
        chain = git["remote", "show", "origin"] | rg["HEAD"]
        logger.debug(f"command: {chain}")
        # This is pretty questionable but it works for now...we find the default
        # branch by looking at which branch HEAD is pointing to
        default_branch = chain().split()[-1].strip()
        logger.debug(f"Default branch is: '{default_branch}'")
        branch_tracking = git[
            "rev-list",
            "--left-right",
            "--count",
            f"upstream/{default_branch}...origin/{default_branch}",
        ]().split()
        git["remote", "update"]()
        commit_count = [int(x.strip()) for x in branch_tracking]
        commits_behind, commits_ahead = commit_count

        logger.info(
            f"Repository {p} is {commits_ahead} commits ahead, {commits_behind} behind",
        )

        # This will return exit code 1 if there's a merge conflict
        git["pull", "upstream", default_branch, "--ff", "--no-commit"].run(
            retcode=(0, 1, 128)
        )
        rm["-rf", "bindings/rust", "Cargo.toml", "Cargo.lock"]()
        git["add", "."]()

        # Check if repo is dirty
        git_status = git["status", "--short"]()
        is_dirty = len(git_status) > 0

        if is_dirty:
            logger.debug("Repo is dirty -- committing changes")
            git["commit", "-m", "'[automated] update to latest upstream'"]()
        else:
            logger.debug("Repo is not dirty")

        git["push"]()
        logger.info(f"Updated repo {p}")


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def updater(path: Path) -> None:
    """Update all repositories recursively in a given path.

    This will perform the usual update steps for all repositories in a given grammar.
    """
    repo_paths = find_git_repositories(path)

    for repo_path in repo_paths:
        try:
            update_grammar_repo(repo_path)
        except ProcessExecutionError as e:
            raise RuntimeError(f"Failed to update {repo_path}") from e


if __name__ == "__main__":
    traceback.install()
    updater()
