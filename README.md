# pyside6-addons-uibcdf

Experimental UIBCDF packaging repo for the third member of the provisional
Qt-for-Python standalone family.

Current scope:

- Linux
- Python 3.13
- target source-build family: 6.10.2

Note:

- the repo still contains bootstrap boundary assets derived from the earlier
  6.9.2 spike environment
- those assets are now historical scaffolding, not the authoritative version
  target for the line we are opening

Role in the family:

- depends on:
  - shiboken6-uibcdf
  - pyside6-essentials-uibcdf
- carries the standalone-critical addon boundary:
  - QtPositioning
  - QtWebChannel
  - QtWebEngine*
  - QtWebEngineProcess
  - WebEngine QML/resources/translations

Current source of truth:

- validated environment:
  /home/diego/Myopt/miniconda3/envs/molsyssuite-qt-spike
- local manifests copied into this repo:
  - manifests/pyside6_addons.files.txt
  - manifests/pyside6_addons.runtime.txt
- standalone-focused reduced manifests:
  - manifests/pyside6_addons_standalone.files.txt
  - manifests/pyside6_addons_standalone.runtime.txt
- upstream codebase reference:
  - ~/repos@others/pyside-setup

Current repo layout:

- upstream pyside6 code is now staged directly in this repo for the Addons line:
  - root build files from `sources/pyside6`
  - `cmake`
  - `libpyside`
  - `libpysideqml`
  - `libpysideremoteobjects`
  - `plugins`
  - `PySide6/glue`, `PySide6/support`, `PySide6/templates`
  - only the runtime-backed module dirs currently needed by the Addons boundary
- packaging/devtools remain repo-local and experimental:
  - `devtools/conda-build`
  - `devtools/conda-envs`
  - `manifests`

First-pass success criteria:

1. package the PySide6_Addons wheel boundary in conda form
2. expose:
   - QtPositioning
   - QtWebChannel
   - QtWebEngineCore
   - QtWebEngineQuick
   - QtWebEngineWidgets
   - QtWebEngineProcess
3. make QWebEngineView importable once the family is installed together

Current packaging approach:

- first pass is manifest-driven rather than source-build-driven
- the current first-pass boundary is intentionally limited to the Python/runtime
  payload staged under `site-packages`
- the default manifest is now the standalone-focused reduced boundary:
  - `WebEngine`
  - `WebChannel`
  - `Positioning`
- wrapper commands under `bin/` are deferred until the core Addons boundary is
  proven
- `devtools/conda-build/build.sh` copies the validated `PySide6_Addons` boundary
  from the known-good environment into `$SP_DIR`
- the source environment can be overridden with:
  - `PYSIDE6_ADDONS_UIBCDF_SOURCE_PREFIX`
- the manifest can also be overridden explicitly with:
  - `PYSIDE6_ADDONS_UIBCDF_MANIFEST`

Current known boundary caveats:

- a few `PySide6/scripts/*` and `PySide6/support/*` references from the wheel
  manifest do not map one-to-one onto the observed source environment layout
- the first-pass recipe therefore focuses on the core Addons runtime boundary
  needed for imports such as `from PySide6.QtWebEngineWidgets import QWebEngineView`
- the full Addons payload is about 400 MB in the validated environment
- the standalone-focused reduced boundary is about 244 MB
- a naive repo-local full-boundary vendoring step is currently unattractive
  because a single file already weighs about 189 MB:
  - `PySide6/Qt/lib/libQt6WebEngineCore.so.6`
