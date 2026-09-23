# pyside6-addons-uibcdf

Experimental, source-built Qt for Python Addons package for the UIBCDF Qt
family. This repository maintains the reduced binding set needed by the
optional MolSysViewer Qt host: QtPositioning, QtWebChannel, and QtWebEngine.
The native Qt Positioning and WebEngine libraries and WebEngine resources are
provided by their separate `qt6-*-uibcdf` packages.

The `python-3.14-qt-6.10.1` branch is a **candidate**, not a public release.
Its Linux-64/Python 3.14 build has passed Conda package tests and a clean
five-package installation. A local HTML page loaded through
`QWebEngineView` under Xvfb with Conda activation, and MolSysViewer's real
Qt transport, window, and opt-in full-render tests passed in a separate
Python 3.14 environment containing the five UIBCDF packages but no canonical
PySide6. A separate local Linux/Python 3.11 regression experiment passed the
five-package clean-install and WebEngine smoke gates, but its recipe is not
yet the checked-in candidate. Python 3.12–3.13 regressions, macOS and Windows
builds, and staged-channel validation remain before broader support or
publication.

The aligned 6.10.1 family is built in dependency order:

1. `shiboken6-uibcdf`
2. `pyside6-essentials-uibcdf`
3. `qt6-positioning-uibcdf` and `qt6-webengine-uibcdf`
4. `pyside6-addons-uibcdf`

The binding source is a selected subset of Qt for Python `pyside-setup`
v6.10.1, with the `PySide6_uibcdf` namespace preserved. The Conda recipe
builds the bindings from source; the old 6.9.2 manifest-driven prototype is
historical, not the current build route. See [devguide](devguide/README.md)
for provenance, local validation, build practices, and release limitations.

Do not run `devtools/conda-build/build-and-upload.sh` for this candidate: it
still represents the older direct-upload route. Publication needs a reviewed,
coordinated family staging/release procedure.

Canonical PySide6 co-installation is a separate future packaging decision:
the Python import namespaces differ already, but some CMake, tool and shared
data installation paths still overlap. See
[`shiboken6-uibcdf#2`](https://github.com/uibcdf/shiboken6-uibcdf/issues/2)
and
[`pyside6-essentials-uibcdf#2`](https://github.com/uibcdf/pyside6-essentials-uibcdf/issues/2).
