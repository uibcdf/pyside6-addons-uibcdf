"""Run tagged MolSysViewer transport probes against the installed Qt host."""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

PROBES = ("_QT_TRANSPORT_SMOKE_SCRIPT", "_QT_TWO_GENERATION_PAYLOAD_SCRIPT")


def load_probe_scripts(test_file: Path) -> dict[str, str]:
    """Read the tagged test probes without importing the source checkout."""

    tree = ast.parse(test_file.read_text(encoding="utf-8"), filename=str(test_file))
    scripts = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Constant):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in PROBES and isinstance(node.value.value, str):
                scripts[target.id] = node.value.value
    if set(scripts) != set(PROBES):
        raise RuntimeError(f"Tagged Viewer tests lack the required Qt probes: {set(PROBES) - set(scripts)}")
    return scripts


def verify_probe_result(name: str, result: subprocess.CompletedProcess[str]) -> None:
    """Require the tagged transport contract, not merely a zero exit code."""

    if result.returncode != 0:
        raise RuntimeError(f"{name} exited {result.returncode}: {result.stderr[-1800:]}")
    if name == PROBES[0]:
        if "TRANSPORT_READY:yes" not in result.stdout:
            raise RuntimeError(f"Viewer event bridge did not become ready: {result.stdout[-1000:]}")
        return
    lines = [line for line in result.stdout.splitlines() if line.startswith("{")]
    if not lines:
        raise RuntimeError(f"Viewer payload bridge produced no report: {result.stderr[-1800:]}")
    report = json.loads(lines[-1])
    if not (
        report.get("first_ok") is True
        and report.get("second_ok") is True
        and report["second_generation"] > report["first_generation"]
        and [(item["label"], item["atoms"]) for item in report["probes"]]
        == [("first", 1), ("second", 2)]
        and len(set(report["served"])) == 2
        and report["failed_deliveries"] == []
    ):
        raise RuntimeError(f"Viewer payload bridge violated its tagged contract: {report}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("test_file", type=Path)
    args = parser.parse_args()
    if not os.environ.get("DISPLAY"):
        raise RuntimeError("Run the installed Viewer probes under xvfb-run or a real display")
    import molsysviewer

    package_path = Path(molsysviewer.__file__).resolve()
    if Path(sys.prefix).resolve() not in package_path.parents:
        raise RuntimeError(f"Viewer resolved outside the installed environment: {package_path}")
    scripts = load_probe_scripts(args.test_file)
    environment = dict(os.environ)
    for key in (
        "QTWEBENGINE_RESOURCES_PATH",
        "QTWEBENGINEPROCESS_PATH",
        "QTWEBENGINE_LOCALES_PATH",
        "QTWEBENGINE_CHROMIUM_FLAGS",
        "QT_QUICK_BACKEND",
    ):
        environment.pop(key, None)
    environment["QT_QPA_PLATFORM"] = "xcb"
    environment["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    for name in PROBES:
        result = subprocess.run(
            [sys.executable, "-c", scripts[name]],
            capture_output=True,
            text=True,
            timeout=90,
            env=environment,
            check=False,
        )
        verify_probe_result(name, result)
        print(f"PASS installed Viewer Qt transport: {name}")


if __name__ == "__main__":
    main()
