"""Componentes reutilizables de interfaz y visualización para páginas Streamlit.

Centraliza patrones comunes (estado del caché en sidebar, manejo amigable cuando
aún no existe caché o falla MongoDB, y figuras vacías de Plotly) para evitar
duplicar código entre `pages/1_Postulantes.py`, `2_Empresas.py` y `3_Eventos.py`.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from cache import CacheNotFoundError
from mongodb import MongoConnectionError


def crear_figura_vacia(
    titulo: str,
    mensaje: str = "No hay datos disponibles para los filtros seleccionados.",
) -> go.Figure:
    """Devuelve una figura Plotly limpia con un mensaje informativo centrado."""
    fig = go.Figure()
    fig.add_annotation(
        text=mensaje,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 14, "color": "#6c757d"},
    )
    fig.update_layout(
        title=titulo,
        xaxis={"visible": False},
        yaxis={"visible": False},
        height=340,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )
    return fig


def render_control_cache_sidebar(
    nombre_modulo: str,
    meta: dict[str, Any],
    actualizar_fn: Callable[[bool], pd.DataFrame],
    key_prefix: str,
) -> None:
    """Muestra en el sidebar el estado del caché en disco y botones de recarga."""
    with st.sidebar:
        st.divider()
        st.subheader(f"📦 Caché: {nombre_modulo}")
        if meta["existe"] and meta["actualizado_en"] is not None:
            fecha_txt = meta["actualizado_en"].strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"Última actualización: {fecha_txt} ({meta['tamano_kb']} KB)")
        else:
            st.caption("Sin caché en disco todavía.")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 MongoDB", key=f"{key_prefix}_refresh_mongo", width="stretch"):
                _ejecutar_actualizacion(actualizar_fn, usar_demo=False, nombre=nombre_modulo)
        with col_b:
            if st.button("🧪 Demo", key=f"{key_prefix}_refresh_demo", width="stretch"):
                _ejecutar_actualizacion(actualizar_fn, usar_demo=True, nombre=nombre_modulo)


def _ejecutar_actualizacion(
    actualizar_fn: Callable[[bool], pd.DataFrame],
    usar_demo: bool,
    nombre: str,
) -> None:
    """Ejecuta la actualización del caché manejando errores de conexión en la UI."""
    try:
        origen = "datos demo" if usar_demo else "MongoDB"
        with st.spinner(f"Actualizando {nombre} desde {origen}..."):
            actualizar_fn(usar_demo)
        st.toast(f"Caché de {nombre} actualizado ({origen}).", icon="✅")
        st.rerun()
    except MongoConnectionError as exc:
        st.error(f"No se pudo conectar a MongoDB: {exc}")
    except Exception as exc:  # pragma: no cover - protección general de UI
        st.error(f"Error inesperado actualizando {nombre}: {exc}")


def cargar_datos_pagina(
    cargar_fn: Callable[[], pd.DataFrame],
    actualizar_fn: Callable[[bool], pd.DataFrame],
    nombre_modulo: str,
    key_prefix: str,
) -> Optional[pd.DataFrame]:
    """Carga el DataFrame cacheado o muestra opciones claras si aún no existe caché."""
    try:
        return cargar_fn()
    except CacheNotFoundError:
        st.warning(
            f"Aún no existe caché generado para **{nombre_modulo}**. "
            "Puedes extraer los datos desde MongoDB o cargar datos de demostración "
            "para probar la plantilla."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                f"🔄 Cargar {nombre_modulo} desde MongoDB",
                key=f"{key_prefix}_init_mongo",
                type="primary",
                width="stretch",
            ):
                _ejecutar_actualizacion(actualizar_fn, usar_demo=False, nombre=nombre_modulo)
        with col2:
            if st.button(
                f"🧪 Cargar datos demo de {nombre_modulo}",
                key=f"{key_prefix}_init_demo",
                width="stretch",
            ):
                _ejecutar_actualizacion(actualizar_fn, usar_demo=True, nombre=nombre_modulo)
        return None
