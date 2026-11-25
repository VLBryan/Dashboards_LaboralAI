"""Visualizaciones Plotly para el dominio de Eventos."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.eventos.metricas import resumen_eventos_por_tipo
from ui_helpers import crear_figura_vacia


def grafico_eventos_por_tipo(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras con volumen de inscritos y asistentes por tipo de evento."""
    resumen = resumen_eventos_por_tipo(df)
    if resumen.empty:
        return crear_figura_vacia("Participación por tipo de evento")

    largo = resumen.melt(
        id_vars="tipo",
        value_vars=["inscritos", "asistentes"],
        var_name="metrica",
        value_name="personas",
    )
    fig = px.bar(
        largo,
        x="tipo",
        y="personas",
        color="metrica",
        barmode="group",
        text="personas",
        title="Inscritos vs Asistentes por tipo de evento",
        labels={"tipo": "Tipo de evento", "personas": "Personas", "metrica": "Métrica"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=360, margin={"t": 50, "b": 30})
    return fig


def grafico_asistencia_eventos(df: pd.DataFrame) -> go.Figure:
    """Gráfico comparativo de tasa de asistencia (%) por evento."""
    if df.empty or "evento" not in df.columns:
        return crear_figura_vacia("Tasa de asistencia por evento")

    ordenado = df.sort_values("tasa_asistencia_pct", ascending=True)
    fig = px.bar(
        ordenado,
        x="tasa_asistencia_pct",
        y="evento",
        orientation="h",
        text="tasa_asistencia_pct",
        title="Tasa de asistencia (%) por evento",
        labels={"evento": "Evento", "tasa_asistencia_pct": "Asistencia (%)"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=360, margin={"t": 50, "b": 30})
    return fig
