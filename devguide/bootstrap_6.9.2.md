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

## Current Packaging Reading

`PySide6_Addons` carries the standalone-critical layer, including:

- `QtPositioning`
- `QtWebChannel`
- `QtWebEngineCore`
- `QtWebEngineQuick`
- `QtWebEngineWidgets`
- `QtWebEngineProcess`
- WebEngine QML/resources/translations

The earlier investigation also showed that naive overlay or pip/conda mixing is
not a stable path. This repo therefore exists so the `Addons` slice can be
packaged as part of an aligned UIBCDF family.

## Expected Dependency Position

`pyside6-addons-uibcdf` depends on:

- `shiboken6-uibcdf`
- `pyside6-essentials-uibcdf`

## First Implementation Checklist

1. copy the validated manifests into `manifests/`
2. vendor the relevant upstream code from `sources/pyside6`
3. isolate the `Addons` slice from the broader upstream tree
4. write a manifest-driven `build.sh`
5. add minimal file/import tests to `meta.yaml`
6. run a temporary `site-packages` smoke check
7. only then attempt a true `conda build`
8. once packaged with the other two repos, test:
   - `from PySide6.QtWebEngineWidgets import QWebEngineView`

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
- keep this note updated whenever the source extraction rule changes
