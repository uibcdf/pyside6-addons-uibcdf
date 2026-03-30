# Compatibility layer for split UIBCDF Qt-for-Python packaging.

function(_uibcdf_define_qt_alias shortname)
    if(TARGET Qt6::${shortname} AND NOT TARGET Qt::${shortname})
        add_library(Qt::${shortname} INTERFACE IMPORTED)
        set_target_properties(Qt::${shortname} PROPERTIES
            INTERFACE_LINK_LIBRARIES "Qt6::${shortname}")
    endif()
    if(TARGET Qt6::${shortname}Private AND NOT TARGET Qt::${shortname}Private)
        add_library(Qt::${shortname}Private INTERFACE IMPORTED)
        set_target_properties(Qt::${shortname}Private PROPERTIES
            INTERFACE_LINK_LIBRARIES "Qt6::${shortname}Private")
    endif()
endfunction()

function(_uibcdf_define_pyside_module_target module)
    if(TARGET ${module})
        return()
    endif()

    if(IS_ABSOLUTE "${PYTHON_SITE_PACKAGES}")
        set(_site_root "${PYTHON_SITE_PACKAGES}")
    else()
        set(_site_root "${CMAKE_INSTALL_PREFIX}/${PYTHON_SITE_PACKAGES}")
    endif()

    set(_pkg_dir "${_site_root}/PySide6")
    if(EXISTS "${_site_root}/${BINDING_NAME}${pyside6_SUFFIX}/${module}${SHIBOKEN_PYTHON_EXTENSION_SUFFIX}")
        set(_pkg_dir "${_site_root}/${BINDING_NAME}${pyside6_SUFFIX}")
    elseif(EXISTS "${_site_root}/PySide6_uibcdf/${module}${SHIBOKEN_PYTHON_EXTENSION_SUFFIX}")
        set(_pkg_dir "${_site_root}/PySide6_uibcdf")
    endif()

    add_library(${module} SHARED IMPORTED)
    set_target_properties(${module} PROPERTIES
        IMPORTED_LOCATION "${_pkg_dir}/${module}${SHIBOKEN_PYTHON_EXTENSION_SUFFIX}"
        INTERFACE_LINK_LIBRARIES "pyside6;Shiboken6::libshiboken")
endfunction()

foreach(_qt_mod Positioning WebEngineCore WebEngineQuick WebEngineWidgets)
    _uibcdf_define_qt_alias(${_qt_mod})
endforeach()

foreach(_py_mod QtCore QtGui QtNetwork QtPrintSupport QtWidgets QtQml QtQuick)
    _uibcdf_define_pyside_module_target(${_py_mod})
endforeach()
