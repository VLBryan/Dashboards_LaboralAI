"""Página independiente del dashboard de Empresas.

Guía para el equipo de Data (Empresas):
- Este archivo pertenece al sub-equipo de Empresas para evitar conflictos en Git Flow.
- La lógica de negocio debe vivir en `src/empresas/`:
  - `cargar_datos.py`: consulta a MongoDB con `@st.cache_data` (solo en memoria).
  - `transformaciones.py`: limpieza y filtros puros.
  - `metricas.py`: KPIs y tablas agregadas.
  - `graficos.py`: figuras Plotly.
"""

from __future__ import annotations

import streamlit as st

from src.empresas import actualizar_cache_empresas, cargar_empresas
from ui_helpers import cargar_df_desde_memoria, render_sidebar_cache_memoria

st.title("🏢 Dashboard Empresas")

render_sidebar_cache_memoria(
    nombre_modulo="Empresas",
    actualizar_fn=actualizar_cache_empresas,
    key_prefix="empresas",
)

# ---------------------------------------------------------------------------
# Guía de inicio rápido para desplegar este dashboard en local:
# Descomenta estas líneas cuando tengas tu `.env` configurado con MongoDB y
# conecta tus funciones de `src/empresas/` (`transformaciones`, `metricas`, `graficos`).
#
# df = cargar_df_desde_memoria(cargar_empresas, "Empresas")
# if df is None or df.empty:
#     st.stop()
# ---------------------------------------------------------------------------
