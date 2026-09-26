"""Guarding the cheap Qt family release preflight against conforming drift."""

import pytest

from devtools.preflight_qt_family import (
    PreflightError,
    _check_recipe,
    _check_source,
    _has_exact_pin,
)


def _addons_metadata():
    pins = [
        "qt6-main =6.10.1",
        "qt6-positioning-uibcdf ==6.10.1",
        "qt6-webengine-uibcdf ==6.10.1",
        "shiboken6-uibcdf ==6.10.1",
        "pyside6-essentials-uibcdf ==6.10.1",
    ]
    return {
        "package": {"name": "pyside6-addons-uibcdf", "version": "6.10.1"},
        "build": {"number": 0},
        "requirements": {
            "host": pins.copy(),
            "run": pins.copy(),
            "run_constrained": ["pyside6 <0"],
        },
        "source": {"path": "../.."},
    }


def test_exact_pin_rejects_a_compatible_range():
    assert _has_exact_pin(["qt6-main =6.10.1"], "qt6-main")
    assert _has_exact_pin(["qt6-main ==6.10.1"], "qt6-main")
    assert not _has_exact_pin(["qt6-main >=6.10.1,<6.11"], "qt6-main")


def test_aligned_addons_recipe_passes():
    _check_recipe("pyside6-addons-uibcdf", _addons_metadata(), "py314h123_0", "3.14")


@pytest.mark.parametrize("section", ["host", "run"])
def test_mixed_qt_line_fails(section):
    metadata = _addons_metadata()
    metadata["requirements"][section][0] = "qt6-main =6.10.2"
    with pytest.raises(PreflightError, match="exact qt6-main=6.10.1"):
        _check_recipe("pyside6-addons-uibcdf", metadata, "py314h123_0", "3.14")


def test_missing_canonical_pyside_conflict_fails():
    metadata = _addons_metadata()
    metadata["requirements"]["run_constrained"] = []
    with pytest.raises(PreflightError, match="solver conflict missing"):
        _check_recipe("pyside6-addons-uibcdf", metadata, "py314h123_0", "3.14")


def test_wrong_python_variant_fails():
    with pytest.raises(PreflightError, match="Python build variant drift"):
        _check_recipe("pyside6-addons-uibcdf", _addons_metadata(), "py313h123_0", "3.14")


def test_changed_build_number_fails():
    metadata = _addons_metadata()
    metadata["build"]["number"] = 1
    with pytest.raises(PreflightError, match="unexpected build number"):
        _check_recipe("pyside6-addons-uibcdf", metadata, "py314h123_1", "3.14")


def test_webengine_source_digest_drift_fails():
    sources = [
        {"path": "../.."},
        {"url": "https://example.org/pyside6_addons-6.10.1.whl", "sha256": "0" * 64},
        {
            "url": "https://example.org/28eb5425c6abef3938fb82a48427d45d1dd4e64f",
            "sha256": "05645440d4177efd3a67992f01c3af65258d43be16b95ab2bd8bb3447db6a155",
        },
    ]
    with pytest.raises(PreflightError, match="download digest drift"):
        _check_source("qt6-webengine-uibcdf", sources)
