# pyside6-addons-uibcdf

Experimental UIBCDF packaging repo for the third member of the provisional
Qt-for-Python standalone family.

Current scope:

- Linux
- Python 3.13
- version family: 6.9.2

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
- local manifests staged in molsysviewer:
  - sandbox/qt_for_python_uibcdf_experiment/manifests/pyside6_addons.files.txt
  - sandbox/qt_for_python_uibcdf_experiment/manifests/pyside6_addons.runtime.txt
- upstream codebase reference:
  - ~/repos@others/pyside-setup

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
