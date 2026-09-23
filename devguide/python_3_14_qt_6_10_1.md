# Python 3.14 / Qt 6.10.1 candidate

Status on 23 September 2026: local Linux-64 candidate built and tested; no
tag, GitHub Release, or Conda upload has been made from this branch.

## Source and boundary

- Qt for Python source: `qt/pyside-setup` tag `v6.10.1`, peeled commit
  `42be1cc7d9973b7da44c048981001b823b329704`, selected paths under
  `sources/pyside6`.
- This fork preserves the `PySide6_uibcdf` namespace and builds only
  `Positioning;WebChannel;WebEngineCore;WebEngineQuick;WebEngineWidgets`.
- The Qt native components are separate exact-version dependencies:
  `qt6-main`, `qt6-positioning-uibcdf`, and `qt6-webengine-uibcdf` 6.10.1.
  Shiboken and Essentials must also be the aligned 6.10.1 candidates.
- The source transition moved generated PySide headers into
  `$PREFIX/PySide6_uibcdf/include`. Addons' CMake discovery was updated to
  match the tested Essentials candidate. The first build failed before this
  correction; the second passed.
- Changes in QtDataVisualization, QtGraphs, and QtMultimedia were not ported:
  those modules are outside this fork's selected build boundary. Their 6.9.2
  files are not evidence of 6.10.1 support.

## Local evidence

- `conda build devtools/conda-build` completed with package tests passing on
  Linux-64/Python 3.14.7. The resulting artifact is
  `pyside6-addons-uibcdf-6.10.1-py314h3fd9d12_0.conda`, SHA-256
  `b2c9d6840619233f6b2f973f8f8dbb2db44e61f90608c8f96b38af23649684bb`.
- A new offline Conda environment resolved the five exact local 6.10.1
  packages plus `qt6-main=6.10.1` and Python 3.14.7. Imports passed for
  QtCore, QtPositioning, QtWebChannel, QtWebEngineCore, and
  QtWebEngineWidgets; `QGeoCoordinate(19.4, -99.1).isValid()` was true.
- With the Conda environment activated, Xvfb available, and test-only
  Chromium flags disabling its sandbox/GPU in this headless CI-like machine,
  `QWebEngineView.loadFinished` reported `True` for a local HTML page.
  Invoking the interpreter without Conda activation missed the WebEngine
  process/resource paths and is not a valid runtime test.
- The machine's system D-Bus socket is absent, causing a Chromium warning;
  the activated Xvfb HTML smoke nevertheless exited successfully.

The reusable smoke is `devtools/smoke_py314.py`. Its WebEngine mode must be
run from an activated Conda environment with a display or Xvfb. The package
does **not** globally disable Chromium sandboxing; the flags above were only
used for this local headless test.

## Remaining gates

1. Run 3.11–3.13 regressions and build/test on each supported platform.
2. Test the actual MolSysViewer optional Qt host against all five packages,
   including resources and a representative viewer workflow.
3. Review the old direct-upload script and release workflow before use. The
   candidate cannot be promoted by treating a successful local build as a
   coordinated family release.
4. Stage the aligned family, run clean-channel installations, and publish only
   after the shared release gates pass.
