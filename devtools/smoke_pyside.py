"""Smoke-test the aligned UIBCDF PySide Addons installation."""

from __future__ import annotations

import argparse
import sys

from PySide6_uibcdf.QtPositioning import QGeoCoordinate
from PySide6_uibcdf.QtWebChannel import QWebChannel
from PySide6_uibcdf.QtWebEngineCore import QWebEngineProfile
from PySide6_uibcdf.QtWebEngineWidgets import QWebEngineView


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--webengine",
        action="store_true",
        help="Load local HTML; requires a display and an activated Conda environment.",
    )
    args = parser.parse_args()

    assert (3, 11) <= sys.version_info[:2] <= (3, 14)
    assert QGeoCoordinate(19.4, -99.1).isValid()
    assert QWebChannel.__module__ == "PySide6.QtWebChannel"
    assert QWebEngineProfile.__module__ == "PySide6.QtWebEngineCore"
    assert QWebEngineView.__module__ == "PySide6.QtWebEngineWidgets"

    if args.webengine:
        from PySide6_uibcdf.QtCore import QTimer
        from PySide6_uibcdf.QtWidgets import QApplication

        app = QApplication([])
        view = QWebEngineView()
        loaded: list[bool] = []
        view.loadFinished.connect(lambda ok: (loaded.append(ok), app.quit()))
        view.setHtml("<h1>Qt WebEngine smoke</h1>")
        QTimer.singleShot(10_000, app.quit)
        app.exec()
        assert loaded == [True], f"HTML did not load successfully: {loaded}"

    print(
        f"PySide6 Addons 6.10.1 / Python {sys.version_info.major}.{sys.version_info.minor} smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
