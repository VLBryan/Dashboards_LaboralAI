"""Extracción y caché de datos para el dominio de Eventos.

Guía para el equipo de Data (Eventos):
- Ajusta los nombres de colecciones (`events`, `eventRegistrations`) y campos en
  `build_eventos()` según el esquema real de tu MongoDB.
- Deja las transformaciones y métricas en `transformaciones.py` y `metricas.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st

from cache import get_cache_metadata, load_df_cache, refresh_module_cache
from config import CACHE_TTL_SECONDS, DB_NAME, get_cache_path
from mongodb import get_collection_df, get_mongo_client, safe_merge

CACHE_PATH: Path = get_cache_path("eventos")


def build_eventos(
    db_name: str = DB_NAME,
    mongo_uri: Optional[str] = None,
) -> pd.DataFrame:
    """Extrae desde MongoDB las colecciones del dominio Eventos y las consolida.

    Por defecto consulta `events` y cruza registros desde `eventRegistrations`.
    """
    with get_mongo_client(mongo_uri) as client:
        eventos = get_collection_df(
            client,
            db_name=db_name,
            coll_name="events",
            projection={
                "title": 1,
                "name": 1,
                "type": 1,
                "category": 1,
                "modality": 1,
                "date": 1,
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

    if eventos.empty:
        return eventos

    if not registros.empty and "event" in registros.columns:
        resumen_reg = (
            registros.groupby("event")
            .agg(
                inscritos=("_id", "count"),
                asistentes=("attended", lambda s: int(s.fillna(False).astype(bool).sum()))
                if "attended" in registros.columns
                else ("_id", "count"),
            )
            .reset_index()
        )
        eventos = safe_merge(eventos, resumen_reg, left_on="_id", right_on="event", how="left")
    else:
        eventos["inscritos"] = 0
        eventos["asistentes"] = 0

    return eventos


def generar_demo_eventos() -> pd.DataFrame:
    """Genera un dataset de demostración para Eventos sin depender de MongoDB."""
    datos = [
        {
            "_id": "ev01",
            "title": "Feria Laboral Tech 2026",
            "type": "Feria",
            "modality": "Virtual",
            "startDate": "2026-09-15",
            "status": "Finalizado",
            "inscritos": 420,
            "asistentes": 310,
        },
        {
            "_id": "ev02",
            "title": "Workshop CV & Entrevistas IA",
            "type": "Workshop",
            "modality": "Virtual",
            "startDate": "2026-10-05",
            "status": "Finalizado",
            "inscritos": 180,
            "asistentes": 145,
        },
        {
            "_id": "ev03",
            "title": "Networking Data & Analytics",
            "type": "Networking",
            "modality": "Presencial",
            "startDate": "2026-10-24",
            "status": "Finalizado",
            "inscritos": 95,
            "asistentes": 82,
        },
        {
            "_id": "ev04",
            "title": "Bootcamp SQL para Analistas",
            "type": "Workshop",
            "modality": "Híbrido",
            "startDate": "2026-11-18",
            "status": "Programado",
            "inscritos": 210,
            "asistentes": 0,
        },
    ]
    return pd.DataFrame(datos)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def cargar_eventos(cache_path: Optional[str] = None) -> pd.DataFrame:
    """Lee el DataFrame de eventos desde disco y lo cachea en memoria de Streamlit."""
    ruta = Path(cache_path) if cache_path else CACHE_PATH
    return load_df_cache(ruta, date_cols=["startDate", "date"])


def actualizar_cache_eventos(
    usar_demo: bool = False,
    cache_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Reconstruye el caché en disco de Eventos e invalida `@st.cache_data`."""
    ruta = cache_path or CACHE_PATH
    builder = generar_demo_eventos if usar_demo else build_eventos
    return refresh_module_cache(
        path=ruta,
        builder_fn=builder,
        clear_streamlit_cache_fn=cargar_eventos.clear,
    )


def obtener_estado_cache_eventos(cache_path: Optional[Path] = None) -> dict[str, Any]:
    """Devuelve metadatos del archivo de caché de Eventos."""
    return get_cache_metadata(cache_path or CACHE_PATH, ttl_seconds=CACHE_TTL_SECONDS)
