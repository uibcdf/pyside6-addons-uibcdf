"""Fail-closed checks for the canonical PySide6 negative solver gate."""

from __future__ import annotations

import subprocess

import pytest

from devtools import check_canonical_conflict as conflict

MANIFEST = {
    "artifacts": {
        "pyside6-addons-uibcdf": {
            "3.11": {"filename": "pyside6-addons-uibcdf-6.10.1-py311test_0.conda"}
        }
    }
}


def _result(code: int, diagnostic: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], code, "", diagnostic)


def test_accepts_positive_canonical_and_negative_mixed_solve(monkeypatch):
    observed = []

    def solve(python_minor, source, packages):
        observed.append((python_minor, source, packages))
        return _result(0) if len(packages) == 1 else _result(1, "Could not solve: pyside6 <0")

    monkeypatch.setattr(conflict, "_solve", solve)
    conflict.validate_conflict(MANIFEST, "3.11", "staging")
    assert observed[1][2] == ["pyside6=6.10.1", "pyside6-addons-uibcdf=6.10.1=py311test_0"]


def test_rejects_missing_canonical_candidate(monkeypatch):
    monkeypatch.setattr(conflict, "_solve", lambda *_: _result(1, "network unavailable"))
    with pytest.raises(RuntimeError, match="availability was not established"):
        conflict.validate_conflict(MANIFEST, "3.11", "staging")


def test_rejects_unexpected_coinstallation(monkeypatch):
    monkeypatch.setattr(conflict, "_solve", lambda *_: _result(0))
    with pytest.raises(RuntimeError, match="unexpectedly resolved"):
        conflict.validate_conflict(MANIFEST, "3.11", "staging")


def test_rejects_nondiagnostic_failure(monkeypatch):
    calls = iter((_result(0), _result(1, "network unavailable")))
    monkeypatch.setattr(conflict, "_solve", lambda *_: next(calls))
    with pytest.raises(RuntimeError, match="without a dependency-conflict diagnosis"):
        conflict.validate_conflict(MANIFEST, "3.11", "staging")
