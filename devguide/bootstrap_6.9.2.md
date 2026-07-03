# Bootstrap 6.9.2

## Scope

This repo currently tracks the first Linux/Python 3.13 experimental UIBCDF line
for `PySide6_Addons` version `6.9.2`.

The repo is no longer only a scaffold. It now contains a first manifest-driven
recipe attempt for the Addons line.

## Why This Repo Exists

This repo owns the standalone-critical slice of the provisional UIBCDF
Qt-for-Python family:

- `shiboken6-uibcdf`
- `pyside6-essentials-uibcdf`
- `pyside6-addons-uibcdf`

`PySide6_Addons` is the package that carries the layer most directly relevant
to the MolSysViewer standalone host.

## Expected Upstream Source

The upstream code should be taken from:

- `/home/diego/repos@others/pyside-setup`

Relevant upstream subtree for this repo:

- `/home/diego/repos@others/pyside-setup/sources/pyside6`

This repo is expected to vendor only the part of that tree needed for the
`PySide6_Addons` slice and build flow.

## Where The Packaging Boundary Came From

The initial boundary reading came from the validated environment:

- `/home/diego/Myopt/miniconda3/envs/molsyssuite-qt-spike`

Current local manifests copied into this repo:

- `manifests/pyside6_addons.files.txt`
- `manifests/pyside6_addons.runtime.txt`

These came from the validated `molsyssuite-qt-spike` environment.

A standalone-focused reduced manifest pair is also now maintained:

- `manifests/pyside6_addons_standalone.files.txt`
- `manifests/pyside6_addons_standalone.runtime.txt`

## Current Packaging Reading

`PySide6_Addons` carries the standalone-critical layer, including:

- `QtPositioning`
- `QtWebChannel`
- `QtWebEngineCore`
- `QtWebEngineQuick`
- `QtWebEngineWidgets`
- `QtWebEngineProcess`
- WebEngine QML/resources/translations

The full observed Addons boundary is large:

- about 400 MB total

The standalone-focused reduced boundary is still substantial, but much more
plausible:

- about 244 MB

That reduced boundary is defined by the pieces explicitly tied to:

- `WebEngine`
- `WebChannel`
- `Positioning`

The earlier investigation also showed that naive overlay or pip/conda mixing is
not a stable path. This repo therefore exists so the `Addons` slice can be
packaged as part of an aligned UIBCDF family.

## Expected Dependency Position

`pyside6-addons-uibcdf` depends on:

- `shiboken6-uibcdf`
- `pyside6-essentials-uibcdf`

## Current Packaging Decision

The first pass remains manifest-driven, but the default boundary is now the
standalone-focused reduced manifest rather than the full Addons payload.

That decision is based on two observations:

1. a family-level smoke already passes with the reduced subset when staging:
   - `shiboken6-uibcdf`
   - `pyside6-essentials-uibcdf`
   - reduced `pyside6-addons-uibcdf`
   into a temporary `site-packages`
2. the full payload includes a single file around 189 MB:
   - `PySide6/Qt/lib/libQt6WebEngineCore.so.6`

This means the reduced manifest is the more realistic candidate for first
public packaging of the standalone family.

## Source Build Fixes Applied (6.9.2)

These issues were discovered and fixed during the first successful source build.
They are documented here so the same fixes can be verified when porting to 6.10.x.

### Fix 1: Essentials include dir path

`cmake/PySideSetup.cmake` computed the path to the installed essentials headers
as `$SP_DIR/PySide6_uibcdf/include`. That path does not exist in a conda build.

The essentials package installs the generated `pyside6_qtXX_python.h` headers
to `$PREFIX/include/PySide6_uibcdf/<ModuleName>/`. The correct cmake variable:

```cmake
set(UIBCDF_PYSIDE_SITE_INCLUDE_DIR
    "${CMAKE_INSTALL_PREFIX}/include/PySide6_uibcdf")
```

The `file(GLOB ...)` loop that follows already walks subdirectories looking for
`pyside6_*_python.h` files and adds those subdirs to the compile include path,
so only the base path needed fixing.

**When upgrading to 6.10.x:** check that `cmake/PySideSetup.cmake` still
contains this path. If upstream changes the essentials install layout, update
accordingly.

### Fix 2: QtWebEngineProcess test path

The recipe test originally checked:

```
test -f "$SP_DIR/PySide6_uibcdf/Qt/libexec/QtWebEngineProcess"
```

That path is the wheel-bundled layout. In a conda build, `QtWebEngineProcess`
is installed by `qt6-webengine-uibcdf` to `$PREFIX/libexec/QtWebEngineProcess`.
Qt itself locates the helper via `QLibraryInfo::LibraryExecutablesPath`, which
resolves to `$PREFIX/libexec/` in a conda environment — no copy or symlink into
the Python package directory is needed.

The corrected test:

```
test -f "$PREFIX/libexec/QtWebEngineProcess"
```

**When upgrading to 6.10.x:** keep this test as-is unless the
`qt6-webengine-uibcdf` install layout changes.


Current upstream subset staged in this repo:

- root build files from `sources/pyside6`
- `cmake`
- `libpyside`
- `libpysideqml`
- `libpysideremoteobjects`
- `plugins`
- `PySide6/glue`, `PySide6/support`, `PySide6/templates`
- runtime-backed module dirs currently imported for the Addons boundary:
  - `Qt3DAnimation`
  - `Qt3DCore`
  - `Qt3DExtras`
  - `Qt3DInput`
  - `Qt3DLogic`
  - `Qt3DRender`
  - `QtBluetooth`
  - `QtCharts`
  - `QtDataVisualization`
  - `QtGraphs`
  - `QtGraphsWidgets`
  - `QtHttpServer`
  - `QtLocation`
  - `QtMultimedia`
  - `QtMultimediaWidgets`
  - `QtNetworkAuth`
  - `QtNfc`
  - `QtPdf`
  - `QtPdfWidgets`
  - `QtPositioning`
  - `QtQuick3D`
  - `QtRemoteObjects`
  - `QtScxml`
  - `QtSensors`
  - `QtSerialBus`
  - `QtSerialPort`
  - `QtSpatialAudio`
  - `QtStateMachine`
  - `QtTextToSpeech`
  - `QtWebChannel`
  - `QtWebEngineCore`
  - `QtWebEngineQuick`
  - `QtWebEngineWidgets`
  - `QtWebSockets`
  - `QtWebView`

## Build Completed (2026-04-04)

Build 3 completed successfully. Validated imports:

```python
from PySide6_uibcdf.QtWebEngineWidgets import QWebEngineView
from PySide6_uibcdf.QtWebChannel import QWebChannel
from PySide6_uibcdf.QtPositioning import QGeoCoordinate
```

All three published to `uibcdf` conda channel as `py313h3fd9d12_3`.

The addons build is fast (~5 min) because it only wraps the WebEngine/WebChannel/Positioning
modules — shiboken does the heavy lifting in essentials.

## Local Build and Upload

### Build (after shiboken6-uibcdf and pyside6-essentials-uibcdf are built)

```bash
cd /path/to/pyside6-addons-uibcdf
conda build devtools/conda-build \
    --channel conda-forge \
    --channel uibcdf \
    --channel local
```

Expected time: ~5 min with CPU_COUNT=14. Peak RAM: ~7 GB.

`--channel local` must include the freshly-built essentials. If essentials was
already uploaded to `uibcdf`, `--channel uibcdf` suffices instead.

### Install locally for testing

```bash
mamba install -n <env> \
    /path/to/conda-bld/linux-64/pyside6-addons-uibcdf-6.9.2-*.conda
```

### Upload

```bash
anaconda upload \
    /path/to/conda-bld/linux-64/pyside6-addons-uibcdf-6.9.2-*.conda \
    --user uibcdf
```

The qt6 helper packages (`qt6-positioning-uibcdf`, `qt6-webengine-uibcdf`) should
be uploaded alongside. They have no Python-version-specific build strings.

### Full release sequence (all 5 packages)

```bash
anaconda upload \
    /path/to/conda-bld/linux-64/shiboken6-uibcdf-6.9.2-*.conda \
    /path/to/conda-bld/linux-64/pyside6-essentials-uibcdf-6.9.2-*.conda \
    /path/to/conda-bld/linux-64/pyside6-addons-uibcdf-6.9.2-*.conda \
    /path/to/conda-bld/linux-64/qt6-positioning-uibcdf-6.9.2-*.conda \
    /path/to/conda-bld/linux-64/qt6-webengine-uibcdf-6.9.2-*.conda \
    --user uibcdf
```

## How To Open A Future 6.10.x Line

1. Validate a coherent 6.10.x family environment first.
2. Regenerate `PySide6_Addons` manifests from that environment.
3. Vendor the matching `sources/pyside6` code.
4. Update this repo's version line and recipe pins.
5. Re-verify both source build fixes (essentials include dir and WebEngineProcess path).
6. Re-run the same manifest-driven smoke path before any release attempt.
7. Test the full family together, not this repo in isolation.

Key things that are unlikely to change between 6.9.2 and 6.10.x for addons:

- `cmake/PySideSetup.cmake` essentials header path (`$PREFIX/include/PySide6_uibcdf`)
- `$PREFIX/libexec/QtWebEngineProcess` location
- The set of modules needed for molsysviewer standalone

## Multi-Python and Multi-Platform

The addons package is the simplest of the three for multi-platform work because
it contains no shiboken patches — it only wraps PySide6 modules.

### Multiple Python versions

Same approach as essentials: change `python =3.13` → target version. No
addons-specific fixes are Python-version-dependent.

### macOS

The `QtWebEngineProcess` is a native macOS executable. Its location may differ
from Linux (`$PREFIX/libexec/` should be the same, but verify with a test build).

QtWebEngine on macOS arm64 (Apple Silicon) is available in Qt 6.6+ and in
conda-forge qt6 packages — but the conda-forge `qt6-webengine` arm64 availability
should be checked before planning this port. In Qt 6.9.x, Chromium (embedded in
QtWebEngine) is officially supported on macOS arm64.

### Windows

QtWebEngine on Windows requires additional system dependencies
(`d3d11`, `d3dcompiler`, `opengl32`). The recipe will need `bld.bat` and the test
commands will need adapting. This is the hardest part of Windows support for this
family.

## Versioning and Build Numbers

Same convention as the rest of the family. Bump `build.number` for any fix;
reset to 0 only on a new upstream version. Keep all three Python-binding packages
synchronized to the same build number.

## Things To Keep Stable

- do not mix `Addons` payloads across family versions
- treat `QWebEngineView` importability as a family-level check
- keep the reduced standalone-focused manifest explicit unless a deliberate
  decision is made to restore the full Addons payload
- keep this note updated whenever the source extraction rule changes
