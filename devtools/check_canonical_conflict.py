"""Prove that canonical PySide6 is available but cannot coexist with UIBCDF Addons."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

import tomllib


def _solve(python_minor: str, source: str, packages: list[str]) -> subprocess.CompletedProcess[str]:
    executable = os.environ.get("MAMBA_EXE")
    if not executable:
        raise RuntimeError("MAMBA_EXE is required for the clean solver probes")
    channels = ["uibcdf/label/staging", "uibcdf", "conda-forge"] if source == "staging" else ["uibcdf", "conda-forge"]
    command = [
        executable,
        "create",
        "--dry-run",
        "--yes",
        "--override-channels",
        "-n",
        f"qt-conflict-probe-{python_minor.replace('.', '')}",
    ]
    for channel in channels:
        command.extend(("-c", channel))
    command.extend((f"python={python_minor}", "qt6-main=6.10.1", *packages))
    return subprocess.run(command, capture_output=True, text=True, timeout=180, check=False)


def validate_conflict(manifest: dict, python_minor: str, source: str) -> None:
    """Require the positive canonical solve and the negative mixed solve."""

    if python_minor not in {"3.11", "3.12", "3.13", "3.14"} or source not in {"staging", "public"}:
        raise ValueError("Unsupported Python minor or package source")
    canonical = _solve(python_minor, source, ["pyside6=6.10.1"])
    if canonical.returncode != 0:
        raise RuntimeError(f"Canonical PySide6 availability was not established: {canonical.stderr[-1200:]}")
    artifact = manifest["artifacts"]["pyside6-addons-uibcdf"][python_minor]
    filename = artifact["filename"]
    prefix = "pyside6-addons-uibcdf-6.10.1-"
    if not filename.startswith(prefix) or not filename.endswith(".conda"):
        raise RuntimeError("Manifest contains an invalid Addons artifact filename")
    build = filename.removeprefix(prefix).removesuffix(".conda")
    mixed = _solve(
        python_minor,
        source,
        ["pyside6=6.10.1", f"pyside6-addons-uibcdf=6.10.1={build}"],
    )
    if mixed.returncode == 0:
        raise RuntimeError("Conda unexpectedly resolved canonical and UIBCDF PySide6 together")
    diagnostic = mixed.stdout + mixed.stderr
    if not re.search(r"could not solve|unsatisfiable|incompatible|conflict|nothing provides", diagnostic, re.IGNORECASE):
        raise RuntimeError(f"Mixed solve failed without a dependency-conflict diagnosis: {diagnostic[-1200:]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", choices=("staging", "public"), required=True)
    parser.add_argument("--python", choices=("3.11", "3.12", "3.13", "3.14"), required=True)
    args = parser.parse_args()
    manifest = tomllib.loads(args.manifest.read_text(encoding="utf-8"))
    validate_conflict(manifest, args.python, args.source)
    print(f"PASS canonical PySide6 6.10.1 conflicts with UIBCDF Addons on Python {args.python}")


if __name__ == "__main__":
    main()
