"""Utilidades y constantes de estilo compartidas por toda la aplicacion."""

COLOR_FONDO = "#f4f1ec"
COLOR_PANEL = "#ffffff"
COLOR_PRIMARIO = "#6b4226"     # marron mueble
COLOR_PRIMARIO_HOVER = "#5a3620"
COLOR_ACENTO = "#c9a26d"       # dorado madera
COLOR_TEXTO = "#2b2b2b"
COLOR_PELIGRO = "#a3372f"
COLOR_EXITO = "#3a7d44"

FUENTE_TITULO = ("Georgia", 20, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12, "bold")
FUENTE_NORMAL = ("Segoe UI", 10)
FUENTE_BOTON = ("Segoe UI", 10, "bold")

ITBIS = 0.18  # 18% impuesto Republica Dominicana


def moneda(valor):
    """Formatea un numero como moneda RD$ 12,345.67"""
    try:
        return f"RD$ {float(valor):,.2f}"
    except (TypeError, ValueError):
        return "RD$ 0.00"
