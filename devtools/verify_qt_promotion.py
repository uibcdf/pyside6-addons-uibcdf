"""Reject a Qt 6.10.1 promotion without the exact successful staging gate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import tomllib

PYTHON_MINORS = ("3.11", "3.12", "3.13", "3.14")
REQUIRED_STEPS = (
    "Verify exact digests, channel, ABI, and installed imports",
    "Reject canonical PySide6 coexistence in the solver",
    "Run local-HTML WebEngine smoke",
    "Run tagged Viewer Qt transport probes under Xvfb",
)


def verify(
    manifest: dict,
    run: dict,
    jobs: dict,
    *,
    candidate_sha: str,
    gate_run_id: int,
    package_spec: str,
    sha256: str,
) -> None:
    """Require one manifest member and the complete exact-commit staging matrix."""

    if not re.fullmatch(r"[0-9a-f]{40}", candidate_sha) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise RuntimeError("Candidate commit or artifact SHA-256 has invalid syntax")
    parts = package_spec.split("/")
    if len(parts) != 5 or parts[0] != "uibcdf" or parts[2:4] != ["6.10.1", "linux-64"]:
        raise RuntimeError("Package spec is outside the Qt 6.10.1 Linux family")
    name, filename = parts[1], parts[4]
    if manifest.get("version") != "6.10.1" or name not in manifest.get("artifacts", {}):
        raise RuntimeError("Package is absent from the release manifest")
    entries = manifest["artifacts"][name]
    if name in {"shiboken6-uibcdf", "pyside6-essentials-uibcdf", "pyside6-addons-uibcdf"}:
        if set(entries) != set(PYTHON_MINORS):
            raise RuntimeError("Release manifest is missing a Python binding cell")
        entries = entries.values()
    else:
        entries = (entries,)
    if not any(item["filename"] == filename and item["sha256"] == sha256 for item in entries):
        raise RuntimeError("Package filename and SHA-256 differ from the release manifest")

    expected_title = f"Qt 6.10.1 staging all at {candidate_sha}"
    if (
        run.get("id") != gate_run_id
        or run.get("event") != "workflow_dispatch"
        or run.get("path") != ".github/workflows/validate_qt_family_staging.yaml"
        or run.get("head_sha") != candidate_sha
        or run.get("display_title") != expected_title
        or run.get("status") != "completed"
        or run.get("conclusion") != "success"
        or not isinstance(run.get("run_attempt"), int)
        or run["run_attempt"] < 1
    ):
        raise RuntimeError("The supplied run is not the successful exact-commit staging gate")
    expected_names = {f"Python {minor} · staging" for minor in PYTHON_MINORS}
    observed = jobs.get("jobs", [])
    if jobs.get("total_count") != 4 or {job.get("name") for job in observed} != expected_names:
        raise RuntimeError("The staging gate does not contain all four Python jobs")
    for job in observed:
        if job.get("conclusion") != "success" or job.get("run_id") != gate_run_id:
            raise RuntimeError(f"Staging job did not succeed: {job.get('name')}")
        step_results = {step.get("name"): step.get("conclusion") for step in job.get("steps", [])}
        if any(step_results.get(name) != "success" for name in REQUIRED_STEPS):
            raise RuntimeError(f"Staging job lacks a successful required check: {job.get('name')}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run-json", type=Path, required=True)
    parser.add_argument("--jobs-json", type=Path, required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--gate-run-id", type=int, required=True)
    parser.add_argument("--package-spec", required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    verify(
        tomllib.loads(args.manifest.read_text(encoding="utf-8")),
        json.loads(args.run_json.read_text(encoding="utf-8")),
        json.loads(args.jobs_json.read_text(encoding="utf-8")),
        candidate_sha=args.candidate_sha,
        gate_run_id=args.gate_run_id,
        package_spec=args.package_spec,
        sha256=args.sha256,
    )
    print(f"PASS exact Qt 6.10.1 staging gate authorizes {args.package_spec}")


if __name__ == "__main__":
    main()
