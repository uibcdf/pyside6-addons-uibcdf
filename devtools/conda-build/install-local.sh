#!/usr/bin/env bash
#
# install-local.sh — build this package from its local conda recipe and install
# it into the active conda environment. For local testing WITHOUT the uibcdf
# conda channel.
#
# This is a COMPILED package (cmake/ninja/clang). It is built LAST: it depends on
# every other package in the family.
#
# Family build order (each repo has its own install-local.sh; run in order — this
# script checks its prerequisites and stops with guidance if you skip one):
#     1. shiboken6-uibcdf
#     2. pyside6-essentials-uibcdf
#     3. qt6-positioning-uibcdf      (repackage: needs external Qt sources)
#     4. qt6-webengine-uibcdf        (repackage: needs external Qt sources)
#     5. pyside6-addons-uibcdf       <-- this repo (needs all of the above)
#
# Usage:
#     conda activate <target-env>
#     ./devtools/conda-build/install-local.sh
#
set -euo pipefail

PKG_NAME="pyside6-addons-uibcdf"
RECIPE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# uibcdf packages that must already be built + installed (in family order).
REQUIRED_PKGS=(shiboken6-uibcdf pyside6-essentials-uibcdf qt6-positioning-uibcdf qt6-webengine-uibcdf)

print_order() {
    cat >&2 <<'EOF'
       Family build order (run each repo's devtools/conda-build/install-local.sh):
         1. shiboken6-uibcdf
         2. pyside6-essentials-uibcdf
         3. qt6-positioning-uibcdf
         4. qt6-webengine-uibcdf
         5. pyside6-addons-uibcdf
EOF
}

if ! conda build --version >/dev/null 2>&1; then
    echo "error: 'conda build' is not available. Install it with:" >&2
    echo "       mamba install -n base conda-build" >&2
    exit 1
fi
if [ -z "${CONDA_PREFIX:-}" ]; then
    echo "error: no active conda environment (activate the target env first)." >&2
    exit 1
fi

missing=()
for pkg in "${REQUIRED_PKGS[@]}"; do
    conda list "$pkg" 2>/dev/null | grep -qE "^${pkg}\s" || missing+=("$pkg")
done
if [ "${#missing[@]}" -gt 0 ]; then
    echo "error: prerequisite package(s) not installed in this env: ${missing[*]}" >&2
    echo "       build them FIRST via their own install-local.sh." >&2
    print_order
    exit 1
fi

echo ">> [${PKG_NAME}] building from recipe: ${RECIPE_DIR}"
conda build "${RECIPE_DIR}" -c local -c conda-forge

echo ">> [${PKG_NAME}] installing into active env: ${CONDA_PREFIX}"
mamba install -y -c local -c conda-forge "${PKG_NAME}"

echo ">> [${PKG_NAME}] done."
