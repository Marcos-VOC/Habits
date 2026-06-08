PALETTE = {
    "azul": "#378ADD",
    "verde": "#639922",
    "teal": "#1D9E75",
    "roxo": "#7F77DD",
    "coral": "#D85A30",
    "rosa": "#D4537E",
    "amarelo": "#BA7517",
    "vermelho": "#E24B4A",
    "cinza": "#888780",
    "ciano": "#0EA5E9",
    "laranja": "#EA580C",
    "lima": "#65A30D",
    "indigo": "#6366F1",
    "esmeralda": "#10B981",
    "fuchsia": "#D946EF",
    "cobre": "#B45309",
}

DEFAULT_COLOR = "azul"


def normalize_color(value: str | None) -> str:
    if value in PALETTE:
        return value
    return DEFAULT_COLOR
