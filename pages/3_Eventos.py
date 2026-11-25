"""Página independiente del dashboard de Eventos.

Guía para el equipo de Data (Eventos):
- Este archivo pertenece al sub-equipo de Eventos para evitar conflictos en Git Flow.
- La lógica de negocio debe vivir en `src/eventos/`:
  - `cargar_datos.py`: consulta a MongoDB con `@st.cache_data` (solo en memoria).
  - `transformaciones.py`: limpieza y filtros puros.
  - `metricas.py`: KPIs y tablas agregadas.
  - `graficos.py`: figuras Plotly.
"""

from __future__ import annotations

import streamlit as st

from src.eventos import actualizar_cache_eventos, cargar_eventos
from ui_helpers import cargar_df_desde_memoria, render_sidebar_cache_memoria

st.title("🎟️ Dashboard Eventos")

render_sidebar_cache_memoria(
    nombre_modulo="Eventos",
    actualizar_fn=actualizar_cache_eventos,
    key_prefix="eventos",
)

# ---------------------------------------------------------------------------
# Guía de inicio rápido para desplegar este dashboard en local:
# Descomenta estas líneas cuando tengas tu `.env` configurado con MongoDB y
# conecta tus funciones de `src/eventos/` (`transformaciones`, `metricas`, `graficos`).
#
# df = cargar_df_desde_memoria(cargar_eventos, "Eventos")
# if df is None or df.empty:
#     st.stop()
# ---------------------------------------------------------------------------
