"""Validate an installed Qt/PySide family against an exact release manifest."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
import sys
from pathlib import Path

import tomllib

FAMILY = (
    "qt6-positioning-uibcdf",
    "qt6-webengine-uibcdf",
    "shiboken6-uibcdf",
    "pyside6-essentials-uibcdf",
    "pyside6-addons-uibcdf",
)
BINDINGS = FAMILY[2:]
PYTHON_MINORS = ("3.11", "3.12", "3.13", "3.14")


def _record(prefix: Path, name: str, version: str) -> dict:
    records = list((prefix / "conda-meta").glob(f"{name}-{version}-*.json"))
    if len(records) != 1:
        raise RuntimeError(f"Expected one Conda record for {name} {version}; found {len(records)}")
    return json.loads(records[0].read_text(encoding="utf-8"))


def _expected_artifact(manifest: dict, name: str, python_minor: str) -> dict:
    artifact = manifest["artifacts"][name]
    return artifact[python_minor] if name in BINDINGS else artifact


def validate_records(prefix: Path, manifest: dict, python_minor: str, source: str) -> None:
    """Require exact artifacts, source labels, and interpreter ABI metadata."""

    if python_minor not in PYTHON_MINORS or source not in {"staging", "public"}:
        raise ValueError("Unsupported Python minor or package source")
    version = manifest["version"]
    if version != "6.10.1":
        raise RuntimeError(f"Unexpected Qt family version: {version}")
    if list((prefix / "conda-meta").glob("pyside6-[0-9]*.json")):
        raise RuntimeError("Canonical pyside6 is installed alongside the UIBCDF family")

    root = "https://conda.anaconda.org/uibcdf"
    if source == "staging":
        root += "/label/staging"
    for name in FAMILY:
        expected = _expected_artifact(manifest, name, python_minor)
        filename = expected["filename"]
        digest = expected["sha256"]
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise RuntimeError(f"Invalid SHA-256 in manifest for {name}")
        record = _record(prefix, name, version)
        if record.get("fn") != filename or record.get("sha256") != digest:
            raise RuntimeError(f"{name} does not match the manifest filename and SHA-256")
        expected_url = f"{root}/linux-64/{filename}"
        if record.get("url") != expected_url:
            raise RuntimeError(f"{name} came from a different Conda artifact URL")
        if record.get("channel") not in {
            root,
            f"{root}/linux-64",
            "uibcdf/label/staging" if source == "staging" else "uibcdf",
            "uibcdf/label/staging/linux-64" if source == "staging" else "uibcdf/linux-64",
        }:
            raise RuntimeError(f"{name} came from a different Conda channel")
        if name in BINDINGS:
            digits = python_minor.replace(".", "")
            if not str(record.get("build", "")).startswith(f"py{digits}"):
                raise RuntimeError(f"{name} has the wrong Python build string")
            depends = record.get("depends", [])
            if not any(dep.startswith(f"python_abi {python_minor}.* *_cp{digits}") for dep in depends):
                raise RuntimeError(f"{name} has the wrong Python ABI")
            if "pyside6 <0" not in record.get("constrains", []):
                raise RuntimeError(f"{name} lacks the canonical PySide6 conflict constraint")

    qt_main = _record(prefix, "qt6-main", version)
    if qt_main.get("version") != version:
        raise RuntimeError("The installed Qt core has a different version")
    for name, expected in (("molsysmt", "0.22.4"), ("molsysviewer", "0.23.4")):
        _record(prefix, name, expected)


def validate_imports(prefix: Path) -> None:
    """Check that the installed Viewer and its Qt bindings resolve inside the environment."""

    import molsysmt
    import molsysviewer
    from molsysviewer import standalone_qt

    for name, module in (("molsysmt", molsysmt), ("molsysviewer", molsysviewer)):
        path = Path(module.__file__).resolve()
        if prefix not in path.parents:
            raise RuntimeError(f"{name} resolved outside the installed environment: {path}")
        if importlib.metadata.version(name) != ("0.22.4" if name == "molsysmt" else "0.23.4"):
            raise RuntimeError(f"{name} has the wrong installed version")
    if not (Path(molsysviewer.__file__).parent / "viewer.js").is_file():
        raise RuntimeError("MolSysViewer's JavaScript bundle is missing")
    standalone_qt._import_qt()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", choices=("staging", "public"), required=True)
    parser.add_argument("--python", choices=PYTHON_MINORS, required=True)
    args = parser.parse_args()
    prefix = Path(sys.prefix).resolve()
    if sys.version_info[:2] != tuple(map(int, args.python.split("."))):
        raise RuntimeError("The active interpreter differs from the requested matrix cell")
    manifest = tomllib.loads(args.manifest.read_text(encoding="utf-8"))
    validate_records(prefix, manifest, args.python, args.source)
    validate_imports(prefix)
    print(f"PASS exact Qt family {args.source} installation on Python {args.python}")


if __name__ == "__main__":
    main()
