"""Visualizaciones Plotly para el dominio de Empresas."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.empresas.metricas import (
    resumen_empresas_por_sector,
    resumen_ofertas_por_tamano,
)
from ui_helpers import crear_figura_vacia


def grafico_empresas_por_sector(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras con cantidad de empresas por sector."""
    resumen = resumen_empresas_por_sector(df)
    if resumen.empty:
        return crear_figura_vacia("Empresas por sector")

    fig = px.bar(
        resumen,
        x="sector",
        y="empresas",
        text="empresas",
        color="sector",
        title="Empresas registradas por sector",
        labels={"sector": "Sector", "empresas": "Empresas"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, height=360, margin={"t": 50, "b": 30})
    return fig


def grafico_ofertas_por_tamano(df: pd.DataFrame) -> go.Figure:
    """Gráfico comparativo de ofertas activas según tamaño de empresa."""
    resumen = resumen_ofertas_por_tamano(df)
    if resumen.empty:
        return crear_figura_vacia("Ofertas activas por tamaño de empresa")

    fig = px.bar(
        resumen,
        x="tamano",
        y="ofertas_activas",
        text="ofertas_activas",
        color="tamano",
        title="Ofertas activas por tamaño de empresa",
        labels={"tamano": "Tamaño", "ofertas_activas": "Ofertas activas"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, height=360, margin={"t": 50, "b": 30})
    return fig
