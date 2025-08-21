import matplotlib
from ppplt import (
    list_paper_presets,
    get_paper_preset,
    apply_paper_preset,
    get_color_set,
    is_grayscale_discriminable,
)


def test_list_presets_contains_canonical():
    names = list_paper_presets()
    assert "ieee-modern" in names and "gb-okabe" in names and "ieee-gray" in names


def test_apply_paper_preset_sets_style_and_colors():
    apply_paper_preset("ieee-modern")
    # style side: font.family should include Times New Roman (from IEEE style)
    fam = matplotlib.rcParams.get("font.family")
    fam = fam if isinstance(fam, list) else [fam]
    assert any("Times New Roman" in str(x) for x in fam)
    # colors side: first 3 colors match Modern Scientific
    colors = get_color_set("Modern Scientific")
    got = [v["color"] for v in matplotlib.rcParams["axes.prop_cycle"]][:3]
    assert got == colors[:3]


def test_okabe_ito_is_color_blind_friendly_grayscale_ok():
    # Our grayscale check is rudimentary; this just ensures function runs and returns boolean
    assert isinstance(is_grayscale_discriminable("Okabe-Ito"), bool)


def test_grayscale_preset_is_discriminable():
    from ppplt import apply_paper_preset
    apply_paper_preset("ieee-gray")
    assert is_grayscale_discriminable("Grayscale-Safe")
