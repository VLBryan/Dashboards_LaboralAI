"""Página independiente del dashboard de Empresas.

Guía para el equipo de Data (Empresas):
- Este archivo pertenece al sub-equipo de Empresas para evitar conflictos en Git Flow.
- Toda la lógica pesada debe vivir en `src/empresas/`.
"""

from __future__ import annotations

import streamlit as st

from src.empresas import (
    actualizar_cache_empresas,
    calcular_kpis_empresas,
    cargar_empresas,
    filtrar_empresas,
    grafico_empresas_por_sector,
    grafico_ofertas_por_tamano,
    obtener_estado_cache_empresas,
    preparar_empresas,
)
from ui_helpers import cargar_datos_pagina, render_control_cache_sidebar

st.title("🏢 Dashboard Empresas")

render_control_cache_sidebar(
    nombre_modulo="Empresas",
    meta=obtener_estado_cache_empresas(),
    actualizar_fn=actualizar_cache_empresas,
    key_prefix="empresas",
)

df_raw = cargar_datos_pagina(
    cargar_fn=cargar_empresas,
    actualizar_fn=actualizar_cache_empresas,
    nombre_modulo="Empresas",
    key_prefix="empresas",
)

if df_raw is None:
    st.stop()

df_prep = preparar_empresas(df_raw)

# -------------------------
# Filtros laterales
# -------------------------
with st.sidebar:
    st.header("🔎 Filtros")
    opciones_sector = sorted(df_prep["sector"].dropna().unique().tolist())
    opciones_tamano = sorted(df_prep["tamano"].dropna().unique().tolist())
    opciones_estado = sorted(df_prep["estado"].dropna().unique().tolist())

    sel_sector = st.multiselect("Sector", opciones_sector)
    sel_tamano = st.multiselect("Tamaño", opciones_tamano)
    sel_estado = st.multiselect("Estado", opciones_estado)

df_filtrado = filtrar_empresas(
    df_prep,
    sectores=sel_sector,
    tamanos=sel_tamano,
    estados=sel_estado,
)

# -------------------------
# KPIs principales
# -------------------------
kpis = calcular_kpis_empresas(df_filtrado)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Empresas", kpis["total_empresas"])
c2.metric("Empresas Activas", kpis["empresas_activas"])
c3.metric("Ofertas Activas", kpis["ofertas_activas"])
c4.metric("Promedio Ofertas / Empresa", kpis["promedio_ofertas"])

# -------------------------
# Gráficos
# -------------------------
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(grafico_empresas_por_sector(df_filtrado), width="stretch")
with g2:
    st.plotly_chart(grafico_ofertas_por_tamano(df_filtrado), width="stretch")

# -------------------------
# Tabla de detalle
# -------------------------
with st.expander("📋 Ver detalle de empresas", expanded=False):
    columnas_vista = [
        c
        for c in ["empresa", "sector", "tamano", "pais", "estado", "ofertas_activas", "ofertas_totales"]
        if c in df_filtrado.columns
    ]
    st.dataframe(df_filtrado[columnas_vista], width="stretch", hide_index=True)
