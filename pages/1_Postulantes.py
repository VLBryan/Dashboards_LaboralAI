"""Página independiente del dashboard de Postulantes.

Guía para el equipo de Data (Postulantes):
- Este archivo pertenece al sub-equipo de Postulantes para evitar conflictos en Git Flow.
- La lógica de negocio debe vivir en `src/postulantes/`:
  - `cargar_datos.py`: consulta a MongoDB con `@st.cache_data` (solo en memoria).
  - `transformaciones.py`: limpieza y filtros puros.
  - `metricas.py`: KPIs y tablas agregadas.
  - `graficos.py`: figuras Plotly.
"""

from __future__ import annotations

import streamlit as st

from src.postulantes import actualizar_cache_postulantes, cargar_postulantes
from ui_helpers import cargar_df_desde_memoria, render_sidebar_cache_memoria

st.title("🧑‍💼 Dashboard Postulantes")

render_sidebar_cache_memoria(
    nombre_modulo="Postulantes",
    actualizar_fn=actualizar_cache_postulantes,
    key_prefix="postulantes",
)

# ---------------------------------------------------------------------------
# Guía de inicio rápido para desplegar este dashboard en local:
# Descomenta estas líneas cuando tengas tu `.env` configurado con MongoDB y
# conecta tus funciones de `src/postulantes/` (`transformaciones`, `metricas`, `graficos`).
#
# df = cargar_df_desde_memoria(cargar_postulantes, "Postulantes")
# if df is None or df.empty:
#     st.stop()
# ---------------------------------------------------------------------------
