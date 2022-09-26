# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Nox sessions."""
import argparse
import re
import subprocess
import tempfile
from typing import List

import nox
from nox.sessions import Session

nox.options.sessions = "lint", "tests", "mypy", "license_check"

# Locations for linting
locations = "src", "tests", "noxfile.py", "docs/conf.py"

package = "pipelines"

_poetry_config_file = "pyproject.toml"


def _remove_extras(constraints_file: str) -> None:
    """Removes extra dependencies from a pip constraints file.

    This is to address pip install not allowing constraints to have extras.
    See https://github.com/pypa/pip/issues/8210.

    Args:
        constraints_file: File containing list of dependency constraints.
    """
    with open(constraints_file, "r") as fp:
        new_deps = []
        pattern = re.compile(r"\[\w+\]")
        for dep in fp.readlines():
            new_dep = pattern.sub("", dep)
            new_deps.append(new_dep)
    with open(constraints_file, "w") as fp:
        fp.writelines(new_deps)


def _install_with_constraints(session: Session, *args: str, **kwargs: str) -> None:
    """Installs packages constrained by Poetry's lock file."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        _remove_extras(requirements.name)
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python=["3.10"])
def tests(session: Session) -> None:
    """Runs the test suite."""
    session.run("poetry", "install", "--no-dev", external=True)
    _install_with_constraints(
        session,
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "freezegun",
    )
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("pytest", *args)


@nox.session(python=["3.10"])
def typeguard(session: Session) -> None:
    """Runtime type checking using typeguard."""
    session.run("poetry", "install", "--no-dev", external=True)
    _install_with_constraints(session, "pytest", "pytest-mock", "typeguard")
    args = session.posargs or ["-m", "not e2e"]
    session.run("pytest", f"--typeguard-packages={package}", *args)


@nox.session(python=["3.10"])
def lint(session: Session) -> None:
    """Lint Python files using flake8."""
    args = session.posargs or locations
    _install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
    )
    session.run("flake8", *args)


@nox.session(python=["3.10"])
def black(session: Session) -> None:
    """Runs black code formatter."""
    _install_with_constraints(session, "black")
    args = session.posargs or locations
    session.run("black", *args)


@nox.session(python=["3.10"])
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    with tempfile.NamedTemporaryFile() as requirements:
        _install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")


@nox.session(python=["3.10"])
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    session.run("poetry", "install", "--no-dev", external=True)
    _install_with_constraints(session, "mypy", "freezegun", "types-PyYAML")
    args = session.posargs or locations
    session.run("mypy", "--show-error-codes", *args)


@nox.session(python=["3.10"])
def xdoctest(session: Session) -> None:
    """Runs examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--no-dev", external=True)
    _install_with_constraints(session, "xdoctest")
    session.run("python", "-m", "xdoctest", package, *args)


@nox.session(python=["3.10"])
def docs(session: Session) -> None:
    """Builds the documentation."""
    session.run("poetry", "install", "--no-dev", external=True)
    _install_with_constraints(session, "sphinx", "sphinx-autodoc-typehints")
    session.run("sphinx-build", "docs", "docs/_build")


@nox.session
def license_check(session: Session) -> None:
    """Checks license headers in code/config files."""
    session.run("bash", "./tests/license/license_check.sh", external=True)


def _get_uncommitted_files() -> List[str]:
    """Returns files that are tracked but haven't been committed using git."""
    output = subprocess.getoutput("git diff --name-only")
    files = [f.strip() for f in output.split("\n")]
    # Remove empty strings
    files = [f for f in files if f]
    return files


def _session_error_uncommitted_files(session: Session, files: List[str]) -> None:
    """Logs a session error showing Git-uncommitted files."""
    files_str = "\n".join(files)
    session.error(f"Uncommitted files found:\n{files_str}")


def _get_current_project_version() -> str:
    """Returns the current version of the project based on the Poetry config file."""
    return subprocess.getoutput("poetry version -s")


def _run_git(session: Session, *args: str, **kwargs: str) -> None:
    session.run("git", external=True, *args, **kwargs)


@nox.session
def release(session: nox.Session) -> None:
    """Kicks off an automated release process by creating and pushing a new tag.

    Usage:
    $ nox -s release -- [major|minor|patch]

    # noqa: DAR101
    """
    uncommitted_files = _get_uncommitted_files()
    if uncommitted_files:
        _session_error_uncommitted_files(session, uncommitted_files)

    parser = argparse.ArgumentParser(description="Release a semver version.")
    parser.add_argument(
        "part",
        type=str,
        nargs=1,
        help="The type of semver release to make.",
        choices={"major", "minor", "patch"},
    )
    args: argparse.Namespace = parser.parse_args(args=session.posargs)
    part: str = args.part.pop()

    # If we get here, we should be good to go
    # Let's do a final check for safety
    confirm = input(
        f"You are about to bump the {part!r} version. Are you sure? [y/n]: "
    )

    # Abort on anything other than 'y'
    if confirm.lower().strip() != "y":
        session.error(f"You said no when prompted to bump the {part!r} version.")

    session.log(f"Bumping the {part!r} version")
    session.run("poetry", "version", part, external=True)

    _run_git(session, "add", _poetry_config_file)
    version = _get_current_project_version()
    session.log(f"Committing version {version}. Not pushing to remote.")
    _run_git(session, "commit", "-m", f"Bump version to {version}")

    # Create and push tag
    session.log("Creating a new tag and pushing to remote")
    _run_git(session, "tag", "-a", version)
    session.run("git", "push", "--tags", external=True)
