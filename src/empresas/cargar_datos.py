"""Extracción desde MongoDB y caché en memoria para Empresas.

Guía para el equipo de Data (Empresas):
- Este archivo es el ÚNICO lugar del módulo que consulta MongoDB.
- Los datos se cachean EXCLUSIVAMENTE en memoria RAM con `@st.cache_data`
  (no se guardan archivos en disco por seguridad de datos sensibles).
- Ajusta los nombres de colecciones y proyecciones en `build_empresas()`
  según tu base MongoDB real.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from cache import invalidar_cache_modulo, registrar_actualizacion_memoria
from config import CACHE_TTL_SECONDS, DB_NAME
from mongodb import get_collection_df, get_mongo_client, safe_merge

MODULO_KEY = "empresas"


def build_empresas(
    db_name: str = DB_NAME,
    mongo_uri: Optional[str] = None,
) -> pd.DataFrame:
    """Consulta MongoDB y construye el DataFrame maestro de Empresas en memoria."""
    with get_mongo_client(mongo_uri) as client:
        empresas = get_collection_df(
            client,
            db_name=db_name,
            coll_name="companies",
            projection={
                "name": 1,
                "sector": 1,
                "size": 1,
                "country": 1,
                "isActive": 1,
                "createdAt": 1,
            },
        )
        vacantes = get_collection_df(
            client,
            db_name=db_name,
            coll_name="jobs",
            projection={"_id": 1, "company": 1, "isActive": 1},
        )
        # Guía: ajusta `coll_name` y añade aquí otras colecciones relacionadas si hace falta.

    return safe_merge(empresas, vacantes, left_on="_id", right_on="company", how="left")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Cargando datos de Empresas...")
def cargar_empresas(db_name: str = DB_NAME) -> pd.DataFrame:
    """Obtiene Empresas desde MongoDB y las mantiene cacheadas solo en memoria."""
    df = build_empresas(db_name=db_name)
    registrar_actualizacion_memoria(MODULO_KEY)
    return df


def actualizar_cache_empresas() -> None:
    """Limpia la caché en memoria de Empresas para forzar relectura desde MongoDB."""
    invalidar_cache_modulo(cargar_empresas, modulo=MODULO_KEY)
