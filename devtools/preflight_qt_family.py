"""Checking the five exact Qt 6.10.1 candidates before expensive builds."""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import subprocess
import tempfile
from pathlib import Path

from conda_build.api import render
from conda_build.config import Config

VERSION = "6.10.1"
BRANCH = "python-3.14-qt-6.10.1"
PYTHON_MINORS = ("3.11", "3.12", "3.13", "3.14")
REPOSITORIES = (
    "qt6-positioning-uibcdf",
    "shiboken6-uibcdf",
    "qt6-webengine-uibcdf",
    "pyside6-essentials-uibcdf",
    "pyside6-addons-uibcdf",
)
BINDINGS = frozenset(
    ("shiboken6-uibcdf", "pyside6-essentials-uibcdf", "pyside6-addons-uibcdf")
)
SIBLING_DEPENDENCIES = {
    "qt6-positioning-uibcdf": (),
    "shiboken6-uibcdf": (),
    "qt6-webengine-uibcdf": ("qt6-positioning-uibcdf",),
    "pyside6-essentials-uibcdf": ("shiboken6-uibcdf",),
    "pyside6-addons-uibcdf": (
        "qt6-positioning-uibcdf",
        "qt6-webengine-uibcdf",
        "shiboken6-uibcdf",
        "pyside6-essentials-uibcdf",
    ),
}
POSITIONING_SOURCE = "11d336c178adf4b8d8f7f8589bb9641bcf4b8eda"
WEBENGINE_SOURCES = {
    "330c229b58d30083a7b99ed22e118eb4f4126408429816a4044ccd0438ae81b4",
    "05645440d4177efd3a67992f01c3af65258d43be16b95ab2bd8bb3447db6a155",
}


class PreflightError(ValueError):
    """Reporting a candidate mismatch before a build starts."""


def _git(directory: Path, *arguments: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(directory), *arguments),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _check_commit(directory: Path, expected: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", expected):
        raise PreflightError(f"{directory.name}: expected commit must be 40 lowercase hex digits")
    actual = _git(directory, "rev-parse", "HEAD")
    if actual != expected:
        raise PreflightError(f"{directory.name}: commit {actual} differs from {expected}")
    branch = _git(directory, "branch", "--show-current")
    if branch != BRANCH:
        raise PreflightError(f"{directory.name}: branch {branch!r} differs from {BRANCH!r}")
    if _git(directory, "status", "--porcelain"):
        raise PreflightError(f"{directory.name}: candidate checkout is dirty")


def _has_exact_pin(requirements: list[str], name: str) -> bool:
    pattern = rf"^{re.escape(name)}\s*={{1,2}}\s*{re.escape(VERSION)}$"
    return any(re.fullmatch(pattern, str(spec)) for spec in requirements)


def _check_source(name: str, source: dict | list) -> None:
    if name == "qt6-positioning-uibcdf":
        if source.get("git_rev") != POSITIONING_SOURCE:
            raise PreflightError(f"{name}: Qt source commit drift")
        if source.get("git_url") != "https://github.com/qt/qtpositioning.git":
            raise PreflightError(f"{name}: Qt source URL drift")
    elif name == "qt6-webengine-uibcdf":
        downloads = [item for item in source if "url" in item]
        if {item.get("sha256") for item in downloads} != WEBENGINE_SOURCES:
            raise PreflightError(f"{name}: upstream download digest drift")
        if not all(VERSION in item["url"] or "28eb5425c6abef3938fb82a48427d45d1dd4e64f" in item["url"] for item in downloads):
            raise PreflightError(f"{name}: upstream version/source URL drift")
    elif source.get("path") != "../..":
        raise PreflightError(f"{name}: binding source must be this exact checkout")


def _check_recipe(name: str, metadata: dict, build_id: str, python_minor: str | None) -> None:
    package = metadata["package"]
    if package.get("name") != name or str(package.get("version")) != VERSION:
        raise PreflightError(f"{name}: package name/version mismatch")
    if str(metadata["build"].get("number")) != "0":
        raise PreflightError(f"{name}: unexpected build number")
    requirements = metadata["requirements"]
    for section in ("host", "run"):
        specs = requirements.get(section, [])
        for dependency in ("qt6-main", *SIBLING_DEPENDENCIES[name]):
            if not _has_exact_pin(specs, dependency):
                raise PreflightError(f"{name}: {section} lacks exact {dependency}={VERSION}")
    if name in BINDINGS:
        if not python_minor or not build_id.startswith("py" + python_minor.replace(".", "")):
            raise PreflightError(f"{name}: Python build variant drift: {build_id}")
        if "pyside6 <0" not in requirements.get("run_constrained", []):
            raise PreflightError(f"{name}: canonical PySide6 solver conflict missing")
    _check_source(name, metadata["source"])


def _render_recipe(directory: Path, python_minor: str, croot: Path) -> tuple[dict, str]:
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            rendered = render(
                directory / "devtools" / "conda-build",
                config=Config(croot=str(croot), python=python_minor),
                finalize=False,
                permit_unsatisfiable_variants=True,
            )
    except Exception as error:
        raise PreflightError(f"{directory.name}: render failed: {error}") from error
    if len(rendered) != 1:
        raise PreflightError(f"{directory.name}: expected one recipe output, got {len(rendered)}")
    candidate = rendered[0][0]
    return candidate.meta, candidate.build_id()


def check_family(root: Path, commits: dict[str, str]) -> list[str]:
    if set(commits) != set(REPOSITORIES):
        raise PreflightError("exactly five named candidate commits are required")
    result: list[str] = []
    with tempfile.TemporaryDirectory(prefix="qt6101-preflight-") as scratch:
        croot = Path(scratch)
        for name in REPOSITORIES:
            directory = root / name
            if not directory.is_dir():
                raise PreflightError(f"missing candidate checkout: {directory}")
            _check_commit(directory, commits[name])
            variants = PYTHON_MINORS if name in BINDINGS else ("3.14",)
            for python_minor in variants:
                metadata, build_id = _render_recipe(directory, python_minor, croot)
                _check_recipe(
                    name,
                    metadata,
                    build_id,
                    python_minor if name in BINDINGS else None,
                )
                result.append(f"{name} {python_minor}: {build_id}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="parent of five checkouts")
    parser.add_argument(
        "--commit",
        action="append",
        required=True,
        metavar="REPOSITORY=SHA",
        help="repeat once for each of the five repositories",
    )
    args = parser.parse_args()
    commits: dict[str, str] = {}
    for item in args.commit:
        if "=" not in item:
            parser.error("each --commit must have REPOSITORY=SHA")
        name, sha = item.split("=", 1)
        if name in commits:
            parser.error(f"duplicate commit for {name}")
        commits[name] = sha
    try:
        lines = check_family(args.root, commits)
    except (PreflightError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print("PASS: exact Qt 6.10.1 family preflight")
    print("\n".join(lines))
    print("Finalized Python ABI, clean installs and runtime gates remain required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
