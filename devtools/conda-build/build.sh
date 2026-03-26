#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "${RECIPE_DIR}/../.." && pwd)"
SOURCE_SITE_PACKAGES="${PYSIDE6_ADDONS_UIBCDF_SOURCE_PREFIX:-/home/diego/Myopt/miniconda3/envs/molsyssuite-qt-spike/lib/python3.13/site-packages}"
MANIFEST="${PYSIDE6_ADDONS_UIBCDF_MANIFEST:-${REPO_ROOT}/manifests/pyside6_addons_standalone.files.txt}"

if [ ! -d "$SOURCE_SITE_PACKAGES" ]; then
    echo "Missing source site-packages: $SOURCE_SITE_PACKAGES" >&2
    exit 1
fi

if [ ! -f "$MANIFEST" ]; then
    echo "Missing manifest: $MANIFEST" >&2
    exit 1
fi

while IFS= read -r relpath; do
    [ -n "$relpath" ] || continue

    case "$relpath" in
        ../../../bin/*)
            continue
            ;;&
        *__pycache__/*|*.pyc)
            continue
            ;;&
    esac

    src="$SOURCE_SITE_PACKAGES/$relpath"
    dst="$SP_DIR/$relpath"

    if [ ! -e "$src" ]; then
        case "$relpath" in
            PySide6/scripts/*)
                echo "Skipping missing script-side manifest entry: $src" >&2
                continue
                ;;&
            PySide6/support/*)
                echo "Skipping missing support-side manifest entry: $src" >&2
                continue
                ;;&
        esac
        echo "Missing manifest entry in source environment: $src" >&2
        exit 1
    fi

    mkdir -p "$(dirname "$dst")"
    cp -a "$src" "$dst"
done < "$MANIFEST"
