# Local Qt/PySide family build practices

This is an operational checkpoint for the experimental UIBCDF Qt 6.10.1
family. It is not a release procedure or evidence that every platform and
Python version is supported.

## Build order and exact inputs

Build `shiboken6-uibcdf` first, then `pyside6-essentials-uibcdf` against that
artifact. Build `qt6-positioning-uibcdf` and `qt6-webengine-uibcdf` against
the same Qt 6.10.1 line. Build `pyside6-addons-uibcdf` last, with all four
earlier artifacts available as explicit local Conda channels, followed by
`conda-forge`. Use `--override-channels`; record which artifacts and hashes
were selected rather than trusting an environment with previously installed
packages. The native Qt packages do not have a Python-minor binding, but the
Shiboken, Essentials, and Addons packages do.

The current `.abi3.so` filenames do **not** make these Conda artifacts
cross-interpreter. The tested `py314` artifacts declare both
`python >=3.14,<3.15.0a0` and `python_abi 3.14.* *_cp314`; changing only the
filename or runtime string would not establish stable-ABI support. Build and
test separate interpreter variants for Python 3.11, 3.12, 3.13, and 3.14
unless a later, explicitly validated packaging contract replaces this one.
Keep the same Python minor in all three binding recipes for a given cell.
The current candidate recipes and some smoke-script names still say 3.14;
a disposable pin substitution is only a regression experiment. Before a
multi-minor release, make package descriptions and smoke names version-neutral
or parameterized and test the resulting actual recipe in every cell.

## Space and parallelism

Check `df -h / /tmp /home` before a local build. On one development host,
`/tmp` shares `/` and had only about 4 GB free, whereas `/home` had ample
space. PySide Essentials' source build and Conda environments occupied more
than 5 GB temporarily, so placing only the final artifact on `/home` is not
enough. Put `CONDA_PKGS_DIRS`, `TMPDIR`, and Conda build's `--croot` on a
filesystem with sufficient free space. For example, after creating the
directories under a task-specific scratch root:

```bash
QT_BUILD_ROOT=/path/on/a/filesystem/with/space
mkdir -p "$QT_BUILD_ROOT/pkgs" "$QT_BUILD_ROOT/tmp"
CONDA_PKGS_DIRS="$QT_BUILD_ROOT/pkgs" \
TMPDIR="$QT_BUILD_ROOT/tmp" \
CPU_COUNT=12 \
conda build devtools/conda-build \
  -c file:///absolute/path/to/required/local/channel \
  -c conda-forge --override-channels \
  --croot "$QT_BUILD_ROOT/component-python-cell"
```

Run that command from the component checkout and add **each** required local
channel for the component; one placeholder channel is not sufficient for
Addons. `CPU_COUNT=12` reflects this host's agreed ceiling, not a universal
recommendation. Choose parallelism according to available cores and memory.
Do not use a repository root or shared cache as a cleanup target. Identify
the exact temporary root, preserve artifact hashes and test results, then
remove only obsolete build intermediates.

## Validation boundary

A successful build is followed by Conda's package tests, then an independent
clean installation of the exact local artifacts and imports. For Addons,
activate the Conda environment before testing WebEngine so its process and
resource paths are available. The real Qt window and rendering gates require
a display or Xvfb; test-only Chromium flags used on a headless host are not
package defaults. Inspect solver provenance and verify that canonical
`pyside6` was not pulled into the intended UIBCDF-only route. Any
co-installation with canonical PySide6 is a separate, tracked packaging
decision, not proof of the UIBCDF-only route.
If Xvfb cannot connect to its display in a restricted execution environment,
check the display permission separately before treating it as a binding or
package failure.

Local Linux results do not replace the supported-platform matrix, staged
channel installs, MolSysViewer integration gate, or coordinated release
decision. Never invoke the old direct-upload script for this candidate.
