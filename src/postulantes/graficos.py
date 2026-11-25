"""Visualizaciones Plotly para el dominio de Postulantes.

Guía para el equipo de Data (Postulantes):
- Cada función recibe un DataFrame ya procesado/resumido y retorna una figura
  `plotly.graph_objects.Figure`.
- Usa `crear_figura_vacia()` cuando el filtro quede sin filas para no romper la UI.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.postulantes.metricas import resumen_por_modalidad, top_profesiones
from ui_helpers import crear_figura_vacia


def grafico_postulantes_por_modalidad(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras con la distribución de postulantes por modalidad."""
    resumen = resumen_por_modalidad(df)
    if resumen.empty:
        return crear_figura_vacia("Postulantes por modalidad")

    fig = px.bar(
        resumen,
        x="modalidad",
        y="cantidad",
        text="cantidad",
        color="modalidad",
        title="Postulantes por modalidad",
        labels={"modalidad": "Modalidad", "cantidad": "Postulantes"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, height=360, margin={"t": 50, "b": 30})
    return fig


def grafico_top_profesiones(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Gráfico horizontal con el Top N de profesiones registradas en CVs."""
    ranking = top_profesiones(df, top_n=top_n)
    if ranking.empty:
        return crear_figura_vacia(f"Top {top_n} profesiones")

    ranking_ordenado = ranking.sort_values("cantidad", ascending=True)
    fig = px.bar(
        ranking_ordenado,
        x="cantidad",
        y="profession",
        orientation="h",
        text="cantidad",
        title=f"Top {top_n} profesiones",
        labels={"profession": "Profesión", "cantidad": "Postulantes"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=360, margin={"t": 50, "b": 30})
    return fig
