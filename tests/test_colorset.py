import matplotlib
from matplotlib import pyplot as plt

from ppplt import (
    list_color_sets,
    get_color_set,
    apply_color_set,
)


def test_list_color_sets_nonempty():
    names = list_color_sets()
    assert len(names) >= 3
    assert "Contrast Set 1" in names


def test_get_color_set_case_insensitive():
    a = get_color_set("contrast set 1")
    b = get_color_set("Contrast Set 1")
    assert a == b
    assert all(isinstance(c, str) and c.startswith("#") for c in a)


def test_apply_color_set_sets_prop_cycle():
    apply_color_set("Contrast Set 2")
    cycle = matplotlib.rcParams.get("axes.prop_cycle")
    # prop_cycle is a Cycler; verify color keys exist and match our set head
    colors = get_color_set("Contrast Set 2")
    # Sample the first 3 colors from the cycle
    got = [v["color"] for v in cycle][:3]
    assert got == colors[:3]


def test_get_color_set_invalid_raises():
    import pytest
    with pytest.raises(ValueError):
        get_color_set("NOT_EXIST")
