from habits.ui.labels import frequency_label


def test_frequency_labels_are_portuguese():
    assert frequency_label("daily") == "Todos os dias"
    assert frequency_label("weekdays") == "Segunda a sexta"
    assert frequency_label("weekly") == "X vezes por semana"
