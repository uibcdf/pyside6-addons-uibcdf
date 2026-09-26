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
PySide6. Separate local Linux/Python 3.11, 3.12, and 3.13 regression
experiments passed five-package clean-install and WebEngine smoke gates.
Those first builds used disposable recipe pin substitutions. The revised
variant-selected Shiboken, Essentials, and Addons recipes have since passed
complete local Python 3.12, 3.13, and 3.14 builds and clean-install
WebEngine smokes. Python 3.11 still needs that final-recipe gate. The first
public candidate is intentionally Linux-64 only; macOS and Windows require
separate work and are not implied by the core MolSysMT/MolSysViewer matrix.
Staged-channel validation is still required before Linux publication.

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

The historical `devtools/conda-build/build-and-upload.sh` entry point now
fails closed. The manual GitHub Actions workflow builds and uploads only to
the `staging` label, from an explicitly named candidate commit. Promotion
to `main` requires a separate exact-artifact decision after the family gate;
see [the build practices](devguide/qt_family_build_practices.md).

Canonical PySide6 co-installation is deliberately unsupported for this 6.10.1
candidate. The Python import namespaces differ, but some CMake, tool and
shared-data paths still overlap; the three binding recipes therefore add a
Conda `run_constrained` conflict with canonical `pyside6`. A future
collision-free design remains tracked in
[`shiboken6-uibcdf#2`](https://github.com/uibcdf/shiboken6-uibcdf/issues/2)
and
[`pyside6-essentials-uibcdf#2`](https://github.com/uibcdf/pyside6-essentials-uibcdf/issues/2).
