import builtins
import importlib
import matplotlib
from matplotlib import pyplot as plt

import ppplt


def test_available_styles_contains_expected():
    styles = set(ppplt.available_styles())
    assert {"IEEE", "GB"}.issubset(styles)


def test_apply_style_ieee_sets_font_family():
    ppplt.apply_style("IEEE")
    fam = matplotlib.rcParams.get("font.family")
    # matplotlib may normalize to list
    if isinstance(fam, str):
        fam = [fam]
    assert any("Times New Roman" == x or "Times New Roman" in str(x) for x in fam)


def test_apply_style_gb_sets_font_family():
    ppplt.apply_style("GB")
    fam = matplotlib.rcParams.get("font.family")
    if isinstance(fam, str):
        fam = [fam]
    assert any("SimSun" == x or "SimSun" in str(x) for x in fam)


def test_apply_style_invalid_raises():
    import pytest

    with pytest.raises(ValueError):
        ppplt.apply_style("UNKNOWN_STYLE")


def test_register_fonts_no_error():
    # Should not raise even if fonts missing in some environments
    ppplt.register_fonts()
