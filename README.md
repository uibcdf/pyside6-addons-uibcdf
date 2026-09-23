# pyside6-addons-uibcdf

Experimental, source-built Qt for Python Addons package for the UIBCDF Qt
family. This repository maintains the reduced binding set needed by the
optional MolSysViewer Qt host: QtPositioning, QtWebChannel, and QtWebEngine.
The native Qt Positioning and WebEngine libraries and WebEngine resources are
provided by their separate `qt6-*-uibcdf` packages.

The `python-3.14-qt-6.10.1` branch is a **candidate**, not a public release.
Its Linux-64/Python 3.14 build has passed Conda package tests and a clean
five-package installation. A local HTML page also loaded through
`QWebEngineView` under Xvfb with Conda activation. Python 3.11–3.13
regression, macOS and Windows builds, and the MolSysViewer application-level
Qt gate remain to be checked before claiming broader support or publishing.

The aligned 6.10.1 family is built in dependency order:

1. `shiboken6-uibcdf`
2. `pyside6-essentials-uibcdf`
3. `qt6-positioning-uibcdf` and `qt6-webengine-uibcdf`
4. `pyside6-addons-uibcdf`

The binding source is a selected subset of Qt for Python `pyside-setup`
v6.10.1, with the `PySide6_uibcdf` namespace preserved. The Conda recipe
builds the bindings from source; the old 6.9.2 manifest-driven prototype is
historical, not the current build route. See [devguide](devguide/README.md)
for provenance, local validation, and release limitations.

Do not run `devtools/conda-build/build-and-upload.sh` for this candidate: it
still represents the older direct-upload route. Publication needs a reviewed,
coordinated family staging/release procedure.
