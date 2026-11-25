"""Página independiente del dashboard de Eventos.

Guía para el equipo de Data (Eventos):
- Este archivo pertenece al sub-equipo de Eventos para evitar conflictos en Git Flow.
- Toda la lógica pesada debe vivir en `src/eventos/`.
"""

from __future__ import annotations

import streamlit as st

from src.eventos import (
    actualizar_cache_eventos,
    calcular_kpis_eventos,
    cargar_eventos,
    filtrar_eventos,
    grafico_asistencia_eventos,
    grafico_eventos_por_tipo,
    obtener_estado_cache_eventos,
    preparar_eventos,
)
from ui_helpers import cargar_datos_pagina, render_control_cache_sidebar

st.title("🎟️ Dashboard Eventos")

render_control_cache_sidebar(
    nombre_modulo="Eventos",
    meta=obtener_estado_cache_eventos(),
    actualizar_fn=actualizar_cache_eventos,
    key_prefix="eventos",
)

df_raw = cargar_datos_pagina(
    cargar_fn=cargar_eventos,
    actualizar_fn=actualizar_cache_eventos,
    nombre_modulo="Eventos",
    key_prefix="eventos",
)

if df_raw is None:
    st.stop()

df_prep = preparar_eventos(df_raw)

# -------------------------
# Filtros laterales
# -------------------------
with st.sidebar:
    st.header("🔎 Filtros")
    opciones_tipo = sorted(df_prep["tipo"].dropna().unique().tolist())
    opciones_mod = sorted(df_prep["modalidad"].dropna().unique().tolist())
    opciones_est = sorted(df_prep["estado"].dropna().unique().tolist())

    sel_tipo = st.multiselect("Tipo de evento", opciones_tipo)
    sel_mod = st.multiselect("Modalidad", opciones_mod)
    sel_est = st.multiselect("Estado", opciones_est)

df_filtrado = filtrar_eventos(
    df_prep,
    tipos=sel_tipo,
    modalidades=sel_mod,
    estados=sel_est,
)

# -------------------------
# KPIs principales
# -------------------------
kpis = calcular_kpis_eventos(df_filtrado)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Eventos", kpis["total_eventos"])
c2.metric("Total Inscritos", kpis["total_inscritos"])
c3.metric("Total Asistentes", kpis["total_asistentes"])
c4.metric("Tasa Asistencia Global", f"{kpis['tasa_asistencia_global']}%")

# -------------------------
# Gráficos
# -------------------------
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(grafico_eventos_por_tipo(df_filtrado), width="stretch")
with g2:
    st.plotly_chart(grafico_asistencia_eventos(df_filtrado), width="stretch")

# -------------------------
# Tabla de detalle
# -------------------------
with st.expander("📋 Ver detalle de eventos", expanded=False):
    columnas_vista = [
        c
        for c in ["evento", "tipo", "modalidad", "estado", "fecha_evento", "inscritos", "asistentes", "tasa_asistencia_pct"]
        if c in df_filtrado.columns
    ]
    st.dataframe(df_filtrado[columnas_vista], width="stretch", hide_index=True)
