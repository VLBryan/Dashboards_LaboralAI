"""Gestión de caché en memoria (`@st.cache_data`) para DataFrames.

Diseño de seguridad y rendimiento:
- Todo el caché vive EXCLUSIVAMENTE en memoria RAM mediante `@st.cache_data` de
  Streamlit; NO se escriben archivos `.csv`, `.pkl` ni `.parquet` en disco para
  proteger datos sensibles de postulantes, empresas y eventos.
- El TTL por defecto se controla desde `config.CACHE_TTL_SECONDS`.
- Usa `invalidar_cache_modulo()` cuando necesites forzar una nueva lectura desde MongoDB.
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

_SESSION_CACHE_KEY = "_estado_cache_memoria"


def _en_contexto_streamlit() -> bool:
    """Verifica si el código corre dentro de una sesión activa de Streamlit."""
    return get_script_run_ctx() is not None


def registrar_actualizacion_memoria(modulo: str) -> None:
    """Guarda en `st.session_state` la marca temporal de la última carga en RAM."""
    if not _en_contexto_streamlit():
        return
    registro = st.session_state.setdefault(_SESSION_CACHE_KEY, {})
    registro[modulo] = datetime.now()


def obtener_actualizacion_memoria(modulo: str) -> Optional[datetime]:
    """Devuelve la fecha/hora de la última consulta registrada en sesión, o None."""
    if not _en_contexto_streamlit():
        return None
    registro = st.session_state.get(_SESSION_CACHE_KEY, {})
    return registro.get(modulo)


def invalidar_cache_modulo(
    cached_loader_fn: Callable[..., object],
    modulo: Optional[str] = None,
) -> None:
    """Limpia la caché en memoria (`@st.cache_data`) de un módulo específico.

    La próxima vez que se llame a `cached_loader_fn()`, volverá a consultar MongoDB.
    """
    clear_fn = getattr(cached_loader_fn, "clear", None)
    if callable(clear_fn):
        clear_fn()

    if modulo and _en_contexto_streamlit():
        registro = st.session_state.get(_SESSION_CACHE_KEY, {})
        registro.pop(modulo, None)
