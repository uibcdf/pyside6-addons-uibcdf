"""Fail-closed checks for exact Qt family Conda promotion."""

from __future__ import annotations

import pytest

from devtools.verify_qt_promotion import PYTHON_MINORS, REQUIRED_STEPS, verify

CANDIDATE = "a" * 40
DIGEST = "b" * 64
RUN_ID = 1234
PACKAGE_SPEC = "uibcdf/qt6-webengine-uibcdf/6.10.1/linux-64/qt6-webengine-uibcdf-6.10.1-0.conda"


def _evidence():
    manifest = {
        "version": "6.10.1",
        "artifacts": {
            "qt6-webengine-uibcdf": {
                "filename": "qt6-webengine-uibcdf-6.10.1-0.conda",
                "sha256": DIGEST,
            }
        },
    }
    run = {
        "id": RUN_ID,
        "event": "workflow_dispatch",
        "path": ".github/workflows/validate_qt_family_staging.yaml",
        "head_sha": CANDIDATE,
        "display_title": f"Qt 6.10.1 staging all at {CANDIDATE}",
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
    }
    jobs = {
        "total_count": 4,
        "jobs": [
            {
                "name": f"Python {minor} · staging",
                "run_id": RUN_ID,
                "conclusion": "success",
                "steps": [{"name": step, "conclusion": "success"} for step in REQUIRED_STEPS],
            }
            for minor in PYTHON_MINORS
        ],
    }
    return manifest, run, jobs


def _verify(manifest, run, jobs):
    verify(
        manifest,
        run,
        jobs,
        candidate_sha=CANDIDATE,
        gate_run_id=RUN_ID,
        package_spec=PACKAGE_SPEC,
        sha256=DIGEST,
    )


def test_accepts_exact_complete_staging_gate():
    _verify(*_evidence())


def test_rejects_wrong_artifact_digest():
    manifest, run, jobs = _evidence()
    manifest["artifacts"]["qt6-webengine-uibcdf"]["sha256"] = "c" * 64
    with pytest.raises(RuntimeError, match="differ from the release manifest"):
        _verify(manifest, run, jobs)


def test_rejects_one_cell_instead_of_full_matrix():
    manifest, run, jobs = _evidence()
    run["display_title"] = f"Qt 6.10.1 staging 3.11 at {CANDIDATE}"
    with pytest.raises(RuntimeError, match="not the successful exact-commit staging gate"):
        _verify(manifest, run, jobs)


def test_rejects_skipped_required_step():
    manifest, run, jobs = _evidence()
    jobs["jobs"][3]["steps"][1]["conclusion"] = "skipped"
    with pytest.raises(RuntimeError, match="lacks a successful required check"):
        _verify(manifest, run, jobs)
