# Qt/PySide 6.10.1 Linux release route

This is the current entry point for the five-package UIBCDF Qt family used by
MolSysViewer's optional standalone Qt host. It is separate from the already
published MolSysMT/MolSysViewer core pair. The first intended publication is
`linux-64` for Python 3.11–3.14; it does not claim a standalone host on macOS
or Windows, or compatibility with canonical `pyside6` in one environment.

## Candidate identity and preflight

Use the `python-3.14-qt-6.10.1` branch in each of these repositories and record
its exact 40-character commit in the release evidence before any build:

1. `qt6-positioning-uibcdf` and `shiboken6-uibcdf`;
2. `qt6-webengine-uibcdf` after Positioning;
3. `pyside6-essentials-uibcdf` after Shiboken;
4. `pyside6-addons-uibcdf` after all four.

Do not combine this line with the 6.9.2 bootstrap or the separate 6.10.2
exploration. Check the five recipes before dispatch: every package version is
6.10.1, every Qt host/runtime pin selects 6.10.1, the sibling package pins
select 6.10.1, and each new candidate has an unused build number. The native
Positioning recipe pins its Qt source commit; the WebEngine recipe pins its
upstream wheel and Qt source with SHA-256. The three binding recipes build
their checked-out source. Render each binding recipe with explicit `--python`
for 3.11, 3.12, 3.13, and 3.14, then inspect its finalized `python` and
`python_abi` requirements; `.abi3.so` filenames alone do not establish one
Conda artifact for all four interpreters. Record the rendered output and
selected channel before paying for a source build.

Run the cheap family preflight from this repository with the parent directory
of five clean checkouts and five recorded commits:

```bash
python devtools/preflight_qt_family.py --root /path/to/checkouts \
  --commit qt6-positioning-uibcdf=<40-hex-sha> \
  --commit shiboken6-uibcdf=<40-hex-sha> \
  --commit qt6-webengine-uibcdf=<40-hex-sha> \
  --commit pyside6-essentials-uibcdf=<40-hex-sha> \
  --commit pyside6-addons-uibcdf=<40-hex-sha>
```

This fast render checks the source/recipe identities and interpreter build
strings without finalizing the Conda dependency solve. Inspect finalized
Python ABI requirements separately before claiming a package cell.

The candidate's GitHub workflow is **manual staging only**. It accepts
`expected_commit` and, for bindings, `python_version`. Its first step fails
if the dispatched branch or checkout differs from the recorded commit. It
uses `uibcdf/action-build-and-upload-conda-packages@v2.2.2` and the
`staging` label, never `main`. The historical direct-upload script fails
closed. No tag or GitHub Release should be created as a way to stage this
family.

Before running a local build, check disk space and allocate package cache,
temporary files, and the Conda build root on a filesystem with room for the
entire Essentials build. Limit this host to at most 12 compilation workers.
The staging workflows use standard hosted Linux runners with four workers
for binding builds; do not assume a self-hosted runner exists in these repos.
See [family build practices](qt_family_build_practices.md) for the exact
scratch layout and runtime lessons.

## Stage and test

Dispatch the existing `build_and_upload_conda_packages.yaml` workflow at
each recorded branch commit. Stage the two native packages once each and
Shiboken, Essentials, and Addons once per Python minor: 14 Linux-64 files
in total. Wait for the upstream staged file before building a dependent
package. A passing Conda build and package test is only producer evidence;
retain its action evidence artifact and independently verify the staged
file identity, hash, build number, and label on Anaconda.org.

For example, the Shiboken 3.11 cell is dispatched with the exact commit
recorded above:

```bash
gh workflow run build_and_upload_conda_packages.yaml \
  --repo uibcdf/shiboken6-uibcdf \
  --ref python-3.14-qt-6.10.1 \
  -f expected_commit=<40-hex-sha> -f python_version=3.11
```

The two native workflows take only `expected_commit`.

For each of Python 3.11–3.14, solve a fresh environment with the staging
channel before public `uibcdf`, then `conda-forge`. Pin all five packages
to 6.10.1 and Qt to 6.10.1. Check the installed `conda-meta` records and
hashes; do not infer provenance just from requested channels or a warm
package cache. Confirm that canonical `pyside6` is absent. In an activated
environment, run the package smoke, an Xvfb WebEngine local-HTML load, and
MolSysViewer's real Qt transport/window integration. Record visible-window
and GPU observations separately from Xvfb evidence. A source/editable
MolSysViewer does not replace a clean installed-package gate.

## Public decision

Promote only after all four staged interpreter cells pass and the
`pyside6 <0` solver conflict is verified: attempting to install canonical
`pyside6` alongside the UIBCDF bindings must fail before files are linked.
Use the `promote@v2.2.2` action with **one exact file identity and
its independently observed SHA-256** per invocation; it adds `main` to the
same bytes rather than rebuilding. Retain every promotion receipt. Repeat
the clean-install and Qt smoke from the public `uibcdf` channel, then create
the five versioned GitHub Releases on their tested commits and update the
Viewer installation instructions. A GitHub Release is not evidence of a
successful Conda promotion or a supported platform by itself.

This is an operational route, not a declaration that the gates have passed.
The active integration work is tracked by
[`uibcdf/pyside6-addons-uibcdf#2`](https://github.com/uibcdf/pyside6-addons-uibcdf/issues/2).
