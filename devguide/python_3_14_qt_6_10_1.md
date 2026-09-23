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
- MolSysViewer's own Linux/Python 3.14.7 real Qt transport, two-generation
  payload, live-window and opt-in full-render tests passed under Xvfb in a
  second environment containing the five UIBCDF Qt packages and no canonical
  `pyside6`. The full Viewer Python suite passed 2,078 tests with 13 skips
  in a separate environment that also had canonical `pyside6=6.10.1`; this
  is useful regression evidence but not the UIBCDF-only package route.
- That coexistence experiment exposed installed-path overlaps with canonical
  PySide6 in the Shiboken and Essentials packages, despite the distinct
  `PySide6_uibcdf` import namespace. The decision to namespace those paths
  or forbid co-installation is tracked in `uibcdf/shiboken6-uibcdf#2` and
  `uibcdf/pyside6-essentials-uibcdf#2`. It does not block the validated
  UIBCDF-only route.

The reusable smoke is now `devtools/smoke_pyside.py`. Its WebEngine mode must be
run from an activated Conda environment with a display or Xvfb. The package
does **not** globally disable Chromium sandboxing; the flags above were only
used for this local headless test.
The revised recipe includes the no-display mode in its Conda package tests;
the HTML-loading mode remains a separate clean-install gate because package
build runners may not provide a display.

## Python 3.11 regression experiment

On 23 September 2026, disposable copies of the three binding recipes changed
their Python host/run pins from 3.14 to 3.11. Shiboken and Essentials built
and passed Conda package tests first. Addons then built against those exact
local channels, plus the same Qt 6.10.1 Positioning and WebEngine artifacts;
its Conda package tests passed. The Addons result is
`pyside6-addons-uibcdf-6.10.1-py311h3fd9d12_0.conda`, SHA-256
`ca933d60220aa7fd54a42d6d63a5d868126779de88a9ef1935d360df8e38964e`.

An independent offline Conda environment installed Python 3.11.16,
`qt6-main=6.10.1`, and the five local UIBCDF packages. Shiboken, QtCore,
QtPositioning, and QtWebEngineWidgets imported; a `QGeoCoordinate` was valid;
canonical `PySide6` was absent. The version-adjusted Addons smoke passed,
including local HTML loading through `QWebEngineView` under Xvfb. The first
Xvfb attempt inside the restricted execution sandbox could not connect to
its display; repeating that test with display permission passed. This was
an execution-environment failure, not a demonstrated package defect.

The same disposable recipe substitution was repeated for Python 3.12 and
3.13, using matching Shiboken and Essentials variants and the same native
Qt Positioning/WebEngine 6.10.1 packages. Both Addons builds passed Conda
package tests. The local Linux-64 artifacts were:

| Python | Addons artifact suffix | SHA-256 |
| --- | --- | --- |
| 3.12 | `py312h3fd9d12_0` | `eadcc3e40d9d70f7de81942e7afb7d41815478432bf62536cf0b39e671131a37` |
| 3.13 | `py313h3fd9d12_0` | `f0247c2f00a2de29424b5664c12967785cc2b3e0fdaf9991ccfcb91d9e8c4f17` |

Independent offline environments selected the three matching local binding
packages plus both native Qt packages, exact `qt6-main=6.10.1`, and the
requested Python minor. Canonical `PySide6` was absent. Imports and
`QGeoCoordinate` checks passed; the version-adjusted Addons smoke loaded
local HTML in `QWebEngineView` under Xvfb for both minors. Chromium D-Bus
and software-rendering warnings were nonfatal. The same evidence had
already passed for 3.11 and 3.14.

These are Linux-64 regression experiments, not additional release
candidates. The branch recipe now selects Python from an explicit Conda
`--python` variant, and the smoke path and output are interpreter-neutral.
A no-download, non-finalized render produced distinct `py311`, `py312`,
`py313`, and `py314` build strings with matching Python host variants. The
revised recipe now includes the no-display Addons smoke in its package tests.

On 23 September 2026, the **revised recipes themselves** were built in
dependency order on Linux-64 with `--python 3.12` and `CPU_COUNT=12`.
Shiboken, Essentials (1,043 compile steps), and Addons (129 steps) each
passed Conda package tests. Their new local artifact SHA-256 values are:

| Binding | Revised-recipe Python 3.12 SHA-256 |
| --- | --- |
| Shiboken | `1faa8deecc53c65b0275c4716e27e50286f6ab5e6ca69f740e979085af8a5887` |
| Essentials | `45a398759f04c24e196e6e2ff82388eb1161a0cc83480c85df14be358d9dfcea` |
| Addons | `edbe013fcac09b0e62e39d3beaa25b696d534b424414d6033c157d8ee8720dbd` |

Finalized metadata for all three requires `python >=3.12,<3.13.0a0` and
`python_abi 3.12.* *_cp312`. Addons also requires the aligned UIBCDF
Shiboken, Essentials, Positioning, and WebEngine packages at 6.10.1.
An independent offline environment installed Python 3.12.14 and the five
local UIBCDF artifacts; canonical `PySide6` was absent. The revised smoke
passed both import/Positioning checks and local HTML loading in WebEngine
under Xvfb. The two native Qt packages and Shiboken/Essentials were
recorded as selected from the indexed local channel. Conda recorded Addons
from its local build directory, whose archive matched the copied channel
artifact byte-for-byte. This is exact local-artifact evidence, **not** a
five-package channel-provenance or staging claim. See
[family build practices](qt_family_build_practices.md) for the build order,
local-channel and disk-space lessons.

## Revised-recipe Linux/Python 3.13 gate

On 23 September 2026, the committed variant-selected Shiboken, Essentials,
and Addons recipes built in dependency order with `conda build --python 3.13`
and `CPU_COUNT=12`. All three Conda package tests passed. The local artifacts
have these SHA-256 values:

| Binding | Revised-recipe Python 3.13 SHA-256 |
| --- | --- |
| Shiboken | `8a944dd7c0fb74d2978d882fe64df519adaf047e17f4176bb24708ce25b183c5` |
| Essentials | `6f63b866862098f8874609260afdc85682b2d93301bd6a44aaa59d916db481db` |
| Addons | `7cf4718bae6bb9e95f1815e50cab711b7a03ac848eff86230a2c4144fcd6ef00` |

Their finalized runtime metadata requires `python >=3.13,<3.14.0a0` and
`python_abi 3.13.* *_cp313`. Essentials and Addons consumed the exact local
Shiboken candidate; Addons also consumed the local Essentials, Positioning,
and WebEngine 6.10.1 artifacts. A fresh offline Conda environment installed
Python 3.13.15, Qt 6.10.1, and all five UIBCDF packages without canonical
`pyside6`. Conda initially attributed Addons to its build directory because
the same bytes were in the package cache; an explicit reinstall from the
indexed local-channel file made all five installed package records name the
local channel. The ordinary smoke passed, and the optional WebEngine smoke
loaded local HTML under Xvfb. Xvfb could not open its display inside the
restricted sandbox, so that display test ran outside it; a nonfatal D-Bus
warning remained. This is a complete **local Linux/Python 3.13 package gate**,
not a staging or public-channel claim.

## Remaining gates

1. Build and test the revised variant-selected recipes on Python 3.11,
   and 3.14; the revised 3.12 and 3.13 cells passed locally. Inspect finalized
   runtime requirements and repeat the clean-install gate on each claimed
   platform.
2. Repeat the MolSysViewer Qt-host gate against exact staged-channel packages
   rather than local artifacts. The local transport, live window, resources,
   and full software-render gate have passed on Linux/Python 3.14.7.
3. Review the old direct-upload script and release workflow before use. The
   candidate cannot be promoted by treating a successful local build as a
   coordinated family release.
4. Stage the aligned family, run clean-channel installations, and publish only
   after the shared release gates pass.
