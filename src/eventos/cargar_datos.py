"""Extracción desde MongoDB y caché en memoria para Eventos.

Guía para el equipo de Data (Eventos):
- Este archivo es el ÚNICO lugar del módulo que consulta MongoDB.
- Los datos se cachean EXCLUSIVAMENTE en memoria RAM con `@st.cache_data`
  (no se guardan archivos en disco por seguridad de datos sensibles).
- Ajusta los nombres de colecciones y proyecciones en `build_eventos()`
  según tu base MongoDB real.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from cache import invalidar_cache_modulo, registrar_actualizacion_memoria
from config import CACHE_TTL_SECONDS, DB_NAME
from mongodb import get_collection_df, get_mongo_client, safe_merge

MODULO_KEY = "eventos"


def build_eventos(
    db_name: str = DB_NAME,
    mongo_uri: Optional[str] = None,
) -> pd.DataFrame:
    """Consulta MongoDB y construye el DataFrame maestro de Eventos en memoria."""
    with get_mongo_client(mongo_uri) as client:
        eventos = get_collection_df(
            client,
            db_name=db_name,
            coll_name="events",
            projection={
                "title": 1,
                "type": 1,
                "modality": 1,
                "startDate": 1,
                "status": 1,
            },
        )
        registros = get_collection_df(
            client,
            db_name=db_name,
            coll_name="eventRegistrations",
            projection={"_id": 1, "event": 1, "attended": 1},
        )
        # Guía: ajusta `coll_name` y añade aquí otras colecciones relacionadas si hace falta.

    return safe_merge(eventos, registros, left_on="_id", right_on="event", how="left")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Cargando datos de Eventos...")
def cargar_eventos(db_name: str = DB_NAME) -> pd.DataFrame:
    """Obtiene Eventos desde MongoDB y los mantiene cacheados solo en memoria."""
    df = build_eventos(db_name=db_name)
    registrar_actualizacion_memoria(MODULO_KEY)
    return df


def actualizar_cache_eventos() -> None:
    """Limpia la caché en memoria de Eventos para forzar relectura desde MongoDB."""
    invalidar_cache_modulo(cargar_eventos, modulo=MODULO_KEY)
