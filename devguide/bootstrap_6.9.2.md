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

## How To Open A Future 6.10.x Line

1. validate a coherent 6.10.x family environment first
2. regenerate `PySide6_Addons` manifests from that environment
3. vendor the matching `sources/pyside6` code
4. update this repo's version line and recipe pins
5. re-run the same manifest-driven smoke path before any release attempt
6. test the full family together, not this repo in isolation only

## Things To Keep Stable

- do not mix `Addons` payloads across family versions
- treat `QWebEngineView` importability as a family-level check
- keep the reduced standalone-focused manifest explicit unless a deliberate
  decision is made to restore the full Addons payload
- keep this note updated whenever the source extraction rule changes

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
