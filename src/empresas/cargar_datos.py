"""Extracción y caché de datos para el dominio de Empresas.

Guía para el equipo de Data (Empresas):
- Ajusta los nombres de colecciones (`companies`, `jobs`) y proyecciones en
  `build_empresas()` según el esquema real de tu base MongoDB.
- No pongas lógica de limpieza ni gráficos aquí; usa `transformaciones.py` y `graficos.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st

from cache import get_cache_metadata, load_df_cache, refresh_module_cache
from config import CACHE_TTL_SECONDS, DB_NAME, get_cache_path
from mongodb import get_collection_df, get_mongo_client, safe_merge

CACHE_PATH: Path = get_cache_path("empresas")


def build_empresas(
    db_name: str = DB_NAME,
    mongo_uri: Optional[str] = None,
) -> pd.DataFrame:
    """Extrae desde MongoDB las colecciones del dominio Empresas y las consolida.

    Por defecto consulta `companies` y agrega conteo de `jobs` por empresa.
    Ajusta `coll_name` y campos si tu base usa otros nombres (p. ej. `vacancies`).
    """
    with get_mongo_client(mongo_uri) as client:
        empresas = get_collection_df(
            client,
            db_name=db_name,
            coll_name="companies",
            projection={
                "name": 1,
                "sector": 1,
                "industry": 1,
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

    if empresas.empty:
        return empresas

    if not vacantes.empty and "company" in vacantes.columns:
        resumen_vacantes = (
            vacantes.groupby("company")
            .agg(
                ofertas_totales=("_id", "count"),
                ofertas_activas=("isActive", lambda s: int(s.fillna(False).astype(bool).sum()))
                if "isActive" in vacantes.columns
                else ("_id", "count"),
            )
            .reset_index()
        )
        empresas = safe_merge(empresas, resumen_vacantes, left_on="_id", right_on="company", how="left")
    else:
        empresas["ofertas_totales"] = 0
        empresas["ofertas_activas"] = 0

    return empresas


def generar_demo_empresas() -> pd.DataFrame:
    """Genera un dataset de demostración para Empresas sin depender de MongoDB."""
    datos = [
        {
            "_id": "e01",
            "name": "TechNova Latam",
            "sector": "Tecnología",
            "size": "51-200",
            "country": "Perú",
            "isActive": True,
            "ofertas_totales": 12,
            "ofertas_activas": 8,
            "createdAt": "2026-08-15",
        },
        {
            "_id": "e02",
            "name": "Finanzas Andinas",
            "sector": "Fintech",
            "size": "201-500",
            "country": "Colombia",
            "isActive": True,
            "ofertas_totales": 9,
            "ofertas_activas": 5,
            "createdAt": "2026-09-04",
        },
        {
            "_id": "e03",
            "name": "EduSpark",
            "sector": "Educación",
            "size": "11-50",
            "country": "Chile",
            "isActive": True,
            "ofertas_totales": 4,
            "ofertas_activas": 3,
            "createdAt": "2026-09-22",
        },
        {
            "_id": "e04",
            "name": "LogiCloud",
            "sector": "Logística",
            "size": "51-200",
            "country": "México",
            "isActive": False,
            "ofertas_totales": 6,
            "ofertas_activas": 0,
            "createdAt": "2026-10-10",
        },
        {
            "_id": "e05",
            "name": "DataPulse AI",
            "sector": "Tecnología",
            "size": "11-50",
            "country": "Perú",
            "isActive": True,
            "ofertas_totales": 7,
            "ofertas_activas": 6,
            "createdAt": "2026-11-05",
        },
    ]
    return pd.DataFrame(datos)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def cargar_empresas(cache_path: Optional[str] = None) -> pd.DataFrame:
    """Lee el DataFrame de empresas desde disco y lo cachea en memoria de Streamlit."""
    ruta = Path(cache_path) if cache_path else CACHE_PATH
    return load_df_cache(ruta, date_cols=["createdAt"])


def actualizar_cache_empresas(
    usar_demo: bool = False,
    cache_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Reconstruye el caché en disco de Empresas e invalida `@st.cache_data`."""
    ruta = cache_path or CACHE_PATH
    builder = generar_demo_empresas if usar_demo else build_empresas
    return refresh_module_cache(
        path=ruta,
        builder_fn=builder,
        clear_streamlit_cache_fn=cargar_empresas.clear,
    )


def obtener_estado_cache_empresas(cache_path: Optional[Path] = None) -> dict[str, Any]:
    """Devuelve metadatos del archivo de caché de Empresas."""
    return get_cache_metadata(cache_path or CACHE_PATH, ttl_seconds=CACHE_TTL_SECONDS)
