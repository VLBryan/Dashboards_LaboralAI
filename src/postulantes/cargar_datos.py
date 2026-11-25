"""Extracción desde MongoDB y caché en memoria para Postulantes.

Guía para el equipo de Data (Postulantes):
- Este archivo es el ÚNICO lugar del módulo que consulta MongoDB.
- Los datos se cachean EXCLUSIVAMENTE en memoria RAM con `@st.cache_data`
  (no se guardan archivos en disco por seguridad de datos sensibles).
- Edita `build_postulantes()` para agregar colecciones, filtros o joins.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from cache import invalidar_cache_modulo, registrar_actualizacion_memoria
from config import CACHE_TTL_SECONDS, DB_NAME
from mongodb import get_collection_df, get_mongo_client, safe_merge

MODULO_KEY = "postulantes"


def build_postulantes(
    db_name: str = DB_NAME,
    mongo_uri: Optional[str] = None,
) -> pd.DataFrame:
    """Consulta MongoDB y construye el DataFrame maestro de Postulantes en memoria."""
    with get_mongo_client(mongo_uri) as client:
        usuarios = get_collection_df(
            client,
            db_name=db_name,
            coll_name="users",
            query={
                "isActive": True,
                "invitationCode": {"$exists": True, "$nin": [None, ""]},
            },
            projection={
                "firstName": 1,
                "lastName": 1,
                "disponibilidad": 1,
                "modalidad": 1,
                "location": 1,
                "rubros": 1,
                "createdAt": 1,
            },
        )
        cvs = get_collection_df(
            client,
            db_name=db_name,
            coll_name="cvs",
            projection={"_id": 0, "user": 1, "profession": 1},
        )
        # Guía: agrega aquí nuevas colecciones (ej. languages) usando get_collection_df(...)

    if not cvs.empty and "user" in cvs.columns:
        cvs = cvs.drop_duplicates(subset=["user"])

    return safe_merge(usuarios, cvs, left_on="_id", right_on="user", how="left")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Cargando datos de Postulantes...")
def cargar_postulantes(db_name: str = DB_NAME) -> pd.DataFrame:
    """Obtiene Postulantes desde MongoDB y los mantiene cacheados solo en memoria."""
    df = build_postulantes(db_name=db_name)
    registrar_actualizacion_memoria(MODULO_KEY)
    return df


def actualizar_cache_postulantes() -> None:
    """Limpia la caché en memoria de Postulantes para forzar relectura desde MongoDB."""
    invalidar_cache_modulo(cargar_postulantes, modulo=MODULO_KEY)
