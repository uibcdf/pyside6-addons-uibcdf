"""Unit tests for fail-closed Qt family installation provenance."""

from __future__ import annotations

import json

import pytest

from devtools.validate_qt_install import BINDINGS, FAMILY, validate_records


def _installation(tmp_path):
    meta = tmp_path / "conda-meta"
    meta.mkdir()
    manifest = {"version": "6.10.1", "artifacts": {}}
    for name in FAMILY:
        filename = f"{name}-6.10.1-test_0.conda"
        artifact = {"filename": filename, "sha256": "a" * 64}
        if name in BINDINGS:
            manifest["artifacts"][name] = {minor: artifact for minor in ("3.11", "3.12", "3.13", "3.14")}
        else:
            manifest["artifacts"][name] = artifact
        record = {
            "name": name,
            "version": "6.10.1",
            "build": "py314test_0" if name in BINDINGS else "test_0",
            "fn": filename,
            "sha256": "a" * 64,
            "url": f"https://conda.anaconda.org/uibcdf/label/staging/linux-64/{filename}",
            "channel": "https://conda.anaconda.org/uibcdf/label/staging",
            "depends": ["python_abi 3.14.* *_cp314"] if name in BINDINGS else [],
            "constrains": ["pyside6 <0"] if name in BINDINGS else [],
        }
        (meta / f"{name}-6.10.1-test_0.json").write_text(json.dumps(record), encoding="utf-8")
    for name, version in (("qt6-main", "6.10.1"), ("molsysmt", "0.22.4"), ("molsysviewer", "0.23.4")):
        (meta / f"{name}-{version}-test_0.json").write_text(
            json.dumps({"name": name, "version": version}), encoding="utf-8"
        )
    return meta, manifest


def test_accepts_exact_staging_records(tmp_path):
    _, manifest = _installation(tmp_path)
    validate_records(tmp_path, manifest, "3.14", "staging")


@pytest.mark.parametrize("field", ["sha256", "fn", "url", "channel"])
def test_rejects_wrong_artifact_identity(tmp_path, field):
    meta, manifest = _installation(tmp_path)
    path = meta / "shiboken6-uibcdf-6.10.1-test_0.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record[field] = "wrong"
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(RuntimeError):
        validate_records(tmp_path, manifest, "3.14", "staging")


def test_rejects_wrong_python_abi(tmp_path):
    meta, manifest = _installation(tmp_path)
    path = meta / "pyside6-addons-uibcdf-6.10.1-test_0.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["depends"] = ["python_abi 3.13.* *_cp313"]
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(RuntimeError, match="Python ABI"):
        validate_records(tmp_path, manifest, "3.14", "staging")


def test_rejects_canonical_pyside(tmp_path):
    meta, manifest = _installation(tmp_path)
    (meta / "pyside6-6.10.1-test_0.json").write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError, match="Canonical pyside6"):
        validate_records(tmp_path, manifest, "3.14", "staging")
