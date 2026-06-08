FREQUENCY_LABELS = {
    "daily": "Todos os dias",
    "weekdays": "Segunda a sexta",
    "weekly": "X vezes por semana",
}


def frequency_label(value: str) -> str:
    return FREQUENCY_LABELS.get(value, value)
