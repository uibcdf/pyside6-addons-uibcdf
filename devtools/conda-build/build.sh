#!/usr/bin/env bash
set -euo pipefail

export LLVM_INSTALL_DIR="${PREFIX}"
export CLANG_INSTALL_DIR="${PREFIX}"
export C_INCLUDE_PATH="${PREFIX}/include${C_INCLUDE_PATH:+:${C_INCLUDE_PATH}}"
export CPLUS_INCLUDE_PATH="${PREFIX}/include${CPLUS_INCLUDE_PATH:+:${CPLUS_INCLUDE_PATH}}"

cmake -S "${SRC_DIR}" -B "${SRC_DIR}/build-conda" -G Ninja \
    -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
    -DCMAKE_PREFIX_PATH="${PREFIX}" \
    -DPython_EXECUTABLE="${PYTHON}" \
    -DPYTHON_SITE_PACKAGES="${SP_DIR}" \
    -DBUILD_TESTS=OFF \
    -DDISABLE_PYI=ON \
    -DMODULES='Positioning;WebChannel;WebEngineCore;WebEngineQuick;WebEngineWidgets'

wrapper="${SRC_DIR}/build-conda/.qfp/bin/shiboken_wrapper.sh"
if [ -f "${wrapper}" ]; then
    python - <<PATCH_WRAPPER
from pathlib import Path
p = Path(${wrapper@Q})
text = p.read_text()
needle = "#!/bin/bash\n"
insert = "#!/bin/bash\nexport LLVM_INSTALL_DIR=${PREFIX@Q}\nexport CLANG_INSTALL_DIR=${PREFIX@Q}\n"
if text.startswith(needle) and "LLVM_INSTALL_DIR" not in text:
    text = insert + text[len(needle):]
    p.write_text(text)
PATCH_WRAPPER
fi

cmake --build "${SRC_DIR}/build-conda" --parallel "${CPU_COUNT:-2}"
cmake --install "${SRC_DIR}/build-conda"
python - <<'PY_RELOCATE'
from pathlib import Path
import os
import shutil

sp = Path(os.environ["SP_DIR"])
canon = sp / "PySide6"
suff = sp / "PySide6_uibcdf"
suff.mkdir(parents=True, exist_ok=True)

def merge_move(src: Path, dst: Path):
    for item in list(src.iterdir()):
        target = dst / item.name
        if item.is_dir():
            if target.exists() and target.is_dir():
                merge_move(item, target)
                item.rmdir()
            elif target.exists():
                item.rename(target.with_name(target.name + '.uibcdf_tmp_conflict'))
                raise RuntimeError(f'conflict moving directory {item} -> {target}')
            else:
                shutil.move(str(item), str(target))
        else:
            if target.exists():
                item.unlink()
            else:
                shutil.move(str(item), str(target))

if canon.exists():
    merge_move(canon, suff)
    if canon.exists():
        try:
            canon.rmdir()
        except OSError:
            pass
PY_RELOCATE
