"""Checks for extracting and validating the tagged Viewer transport probes."""

from __future__ import annotations

import json
import subprocess

import pytest

from devtools.verify_viewer_qt_transport import (
    PROBES,
    load_probe_scripts,
    verify_probe_result,
)


def test_loads_only_the_two_named_tagged_probes(tmp_path):
    test_file = tmp_path / "test_standalone.py"
    test_file.write_text(
        '_QT_TRANSPORT_SMOKE_SCRIPT = r"print(1)"\n'
        '_QT_TWO_GENERATION_PAYLOAD_SCRIPT = r"print(2)"\n'
        'raise RuntimeError("Never import this file")\n',
        encoding="utf-8",
    )
    assert load_probe_scripts(test_file) == {
        PROBES[0]: "print(1)",
        PROBES[1]: "print(2)",
    }


def test_rejects_missing_tagged_probe(tmp_path):
    test_file = tmp_path / "test_standalone.py"
    test_file.write_text('_QT_TRANSPORT_SMOKE_SCRIPT = "ok"\n', encoding="utf-8")
    with pytest.raises(RuntimeError, match="lack the required Qt probes"):
        load_probe_scripts(test_file)


def test_event_probe_requires_ready_marker():
    with pytest.raises(RuntimeError, match="did not become ready"):
        verify_probe_result(PROBES[0], subprocess.CompletedProcess([], 0, "", ""))


def test_payload_probe_requires_two_deliveries():
    report = {
        "first_ok": True,
        "second_ok": True,
        "first_generation": 1,
        "second_generation": 2,
        "probes": [{"label": "first", "atoms": 1}, {"label": "second", "atoms": 2}],
        "served": ["one", "two"],
        "failed_deliveries": [],
    }
    verify_probe_result(PROBES[1], subprocess.CompletedProcess([], 0, json.dumps(report), ""))
    report["failed_deliveries"] = ["error"]
    with pytest.raises(RuntimeError, match="violated"):
        verify_probe_result(PROBES[1], subprocess.CompletedProcess([], 0, json.dumps(report), ""))
