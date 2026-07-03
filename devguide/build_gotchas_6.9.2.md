# Build gotchas — 6.9.2

Notes for building `pyside6-addons-uibcdf`. The full story is in the
`pyside6-essentials-uibcdf` repo's `devguide/build_gotchas_6.9.2.md`; this repo
mostly got it right already, but the same rules apply.

## `-DMODULES` is required and must be ordered

Addons already builds a **whitelisted** module set:

```
-DMODULES='Positioning;WebChannel;WebEngineCore;WebEngineQuick;WebEngineWidgets'
```

This is what essentials was missing (and why essentials `_4` picked up a leaked
WebEngine and failed — see the essentials gotchas doc). Keep this list, and keep
it in **dependency order**: `WebEngineCore` before `WebEngineQuick` /
`WebEngineWidgets` (they include WebEngineCore's generated header). `Positioning`
and `WebChannel` depend only on host modules (Core/Qml/Widgets), which come from
the installed `pyside6-essentials-uibcdf`.

## Host dependencies must be built first

Addons requires, in its host env, the freshly-built family: `shiboken6-uibcdf *_4`,
`pyside6-essentials-uibcdf *_4`, `qt6-positioning-uibcdf` and `qt6-webengine-uibcdf`.
Build the family in order (see `build-and-upload.sh` header) so these are in the
local channel before addons builds. `CMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY` /
`CMAKE_FIND_USE_PACKAGE_REGISTRY=OFF` in the recipe are kept as conda-build hygiene
so addons links WebEngine/Positioning from its **own** host env, not from whatever
is installed in the active env.
