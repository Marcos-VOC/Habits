from habits.palette import normalize_color


def test_normalize_color_is_case_insensitive():
    assert normalize_color("Azul") == "azul"
    assert normalize_color("AZUL") == "azul"
    assert normalize_color(" ciano ") == "ciano"
    assert normalize_color("inexistente") == "azul"
