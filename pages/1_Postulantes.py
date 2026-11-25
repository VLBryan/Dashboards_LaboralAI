"""Página independiente del dashboard de Postulantes.

Guía para el equipo de Data (Postulantes):
- Este archivo pertenece al sub-equipo de Postulantes para evitar conflictos en Git Flow.
- La lógica de negocio debe vivir en `src/postulantes/` (`cargar_datos.py`,
  `transformaciones.py`, `metricas.py`, `graficos.py`); aquí solo se orquestan filtros y UI.
"""

from __future__ import annotations

import streamlit as st

from src.postulantes import (
    actualizar_cache_postulantes,
    calcular_kpis_postulantes,
    cargar_postulantes,
    filtrar_postulantes,
    grafico_postulantes_por_modalidad,
    grafico_top_profesiones,
    obtener_estado_cache_postulantes,
    preparar_postulantes,
)
from ui_helpers import cargar_datos_pagina, render_control_cache_sidebar

st.title("🧑‍💼 Dashboard Postulantes")

render_control_cache_sidebar(
    nombre_modulo="Postulantes",
    meta=obtener_estado_cache_postulantes(),
    actualizar_fn=actualizar_cache_postulantes,
    key_prefix="postulantes",
)

df_raw = cargar_datos_pagina(
    cargar_fn=cargar_postulantes,
    actualizar_fn=actualizar_cache_postulantes,
    nombre_modulo="Postulantes",
    key_prefix="postulantes",
)

if df_raw is None:
    st.stop()

df_prep = preparar_postulantes(df_raw)

# -------------------------
# Filtros laterales
# -------------------------
with st.sidebar:
    st.header("🔎 Filtros")
    opciones_modalidad = sorted(df_prep["modalidad"].dropna().unique().tolist())
    opciones_disp = sorted(df_prep["disponibilidad"].dropna().unique().tolist())
    opciones_prof = sorted(df_prep["profession"].dropna().unique().tolist())

    sel_modalidad = st.multiselect("Modalidad", opciones_modalidad)
    sel_disp = st.multiselect("Disponibilidad", opciones_disp)
    sel_prof = st.multiselect("Profesión", opciones_prof)

df_filtrado = filtrar_postulantes(
    df_prep,
    modalidades=sel_modalidad,
    disponibilidades=sel_disp,
    profesiones=sel_prof,
)

# -------------------------
# KPIs principales
# -------------------------
kpis = calcular_kpis_postulantes(df_filtrado)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Postulantes", kpis["total_postulantes"])
c2.metric("Con CV / Profesión", kpis["con_cv"], f"{kpis['porcentaje_cv']}%")
c3.metric("Profesiones únicas", kpis["profesiones_unicas"])
c4.metric("Modalidad principal", kpis["modalidad_principal"])

# -------------------------
# Gráficos
# -------------------------
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(grafico_postulantes_por_modalidad(df_filtrado), width="stretch")
with g2:
    st.plotly_chart(grafico_top_profesiones(df_filtrado, top_n=10), width="stretch")

# -------------------------
# Tabla de detalle
# -------------------------
with st.expander("📋 Ver detalle de postulantes", expanded=False):
    columnas_vista = [
        c
        for c in ["nombre_completo", "profession", "modalidad", "disponibilidad", "ubicacion", "cantidad_rubros"]
        if c in df_filtrado.columns
    ]
    st.dataframe(df_filtrado[columnas_vista], width="stretch", hide_index=True)
