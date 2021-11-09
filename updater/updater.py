"""A script that recursively updates all repositories in a path.

Given a path, this script will find all of the valid git repositories under it, and then pull the
default branch from upstream, and then delete any Rust bindings in the repository.
"""

from typing import List
import click
from pathlib import Path
import logging
from rich.logging import RichHandler
import subprocess
from plumbum import local

FORMAT = "%(message)s"


def _cmd(args: List[str]) -> subprocess.CompletedProcess[bytes]:
    """Wrapper over subprocess.

    Args:
        args: The arguments to pass to the subprocess call.

    Returns:
        Return the results.
    """
    results = subprocess.run(args, shell=True, check=True)
    return results


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
            logging.info("Found repo %s", repo_path)
            child_repos.append(repo_path)
    return child_repos


def update_grammar_repo(p: Path) -> None:
    """Update the repository for a grammar.

    Args:
        p: The path to a repository root for a tree-sitter grammar.
    """
    logging.debug("Updating repo %s", p)

    # * clean the local repository -- done
    # * get the default branch
    # * check if upstream has updates
    # * merge without commit
    # * force remove rust bindings
    # * add everything
    # * commit merge

    with local.cwd(p):
        # Clean the local repository before merging
        git = local["git"]
        rg = local["rg"]
        res = git["clean", "-f", "-d"]()

        # Get the default branch (since people will use "main" or "master" generally
        chain = git["remote", "show", "origin"] | rg["HEAD"]
        logging.debug(f"command: {chain}")
        # This is pretty questionable but it works for now...we find the default
        # branch by looking at which branch HEAD is pointing to
        default_branch = chain().split()[-1].strip()
        logging.debug("Default branch is: '%s'", default_branch)
        branch_tracking = git[
            "rev-list",
            "--left-right",
            "--count",
            f"upstream/{default_branch}...origin/{default_branch}",
        ]().split()
        git["remote", "update"]()
        commit_count = [int(x.strip()) for x in branch_tracking]
        commits_behind, commits_ahead = commit_count

        if commits_behind == 0:
            logging.info("Repository %s is up to date", p)
            return

        logging.info(
            "Repository %s is up to %d commits ahead, %d behind",
            p,
            commits_ahead,
            commits_behind,
        )
        # TODO(afnan) continue from here


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def updater(path: Path):
    """Update all repositories recursively in a given path.

    This will perform the usual update steps for all repositories in a given grammar.
    """
    repo_paths = find_git_repositories(path)

    for repo_path in repo_paths:
        update_grammar_repo(repo_path)


if __name__ == "__main__":
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
    updater()