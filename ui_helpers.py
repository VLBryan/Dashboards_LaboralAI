"""Componentes reutilizables mínimos para las páginas Streamlit.

Centraliza la gestión visual del caché en memoria en el sidebar y la carga
protegida desde MongoDB para evitar duplicar boilerplate en `pages/`.
"""

from __future__ import annotations

from typing import Callable, Optional

import pandas as pd
import streamlit as st

from cache import obtener_actualizacion_memoria
from mongodb import MongoConnectionError


def render_sidebar_cache_memoria(
    nombre_modulo: str,
    actualizar_fn: Callable[[], None],
    key_prefix: str,
) -> None:
    """Muestra en el sidebar el botón para limpiar/recargar el caché en memoria."""
    with st.sidebar:
        st.divider()
        st.caption(f"⚡ Caché en memoria: **{nombre_modulo}**")
        ultima = obtener_actualizacion_memoria(key_prefix)
        if ultima is not None:
            st.caption(f"Última lectura: {ultima.strftime('%H:%M:%S')}")

        if st.button(
            "🔄 Actualizar datos (MongoDB)",
            key=f"{key_prefix}_clear_cache",
            width="stretch",
        ):
            actualizar_fn()
            st.toast(f"Caché en memoria de {nombre_modulo} limpiado.", icon="🔄")
            st.rerun()


def cargar_df_desde_memoria(
    cargar_fn: Callable[[], pd.DataFrame],
    nombre_modulo: str,
) -> Optional[pd.DataFrame]:
    """Ejecuta el cargador cacheado en RAM manejando errores de conexión de forma limpia."""
    try:
        return cargar_fn()
    except MongoConnectionError as exc:
        st.warning(
            f"No se pudo conectar a MongoDB para **{nombre_modulo}**. "
            "Verifica tu archivo `.env` y la conexión de red."
        )
        st.caption(f"Detalle técnico: {exc}")
        return None
