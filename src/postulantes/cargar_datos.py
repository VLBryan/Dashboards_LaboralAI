"""Extracción y caché de datos para el dominio de Postulantes.

Guía para el equipo de Data (Postulantes):
- Este archivo es el ÚNICO lugar del módulo que habla con MongoDB y el disco.
- Edita `build_postulantes()` cuando agregues nuevas colecciones o campos.
- Mantén la lógica de limpieza y columnas derivadas en `transformaciones.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st

from cache import get_cache_metadata, load_df_cache, refresh_module_cache
from config import CACHE_TTL_SECONDS, DB_NAME, get_cache_path
from mongodb import get_collection_df, get_mongo_client, safe_merge

CACHE_PATH: Path = get_cache_path("postulantes")


def build_postulantes(
    db_name: str = DB_NAME,
    mongo_uri: Optional[str] = None,
) -> pd.DataFrame:
    """Extrae desde MongoDB las colecciones necesarias para Postulantes y las une.

    Retorna el DataFrame maestro listo para guardarse en el caché de disco.
    """
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
        # Guía: Si luego necesitas idiomas u otra colección, agrégala aquí:
        # idiomas = get_collection_df(client, db_name, "languages", projection={"_id": 0, "user": 1, "language": 1})

    # Si un usuario tiene múltiples CVs, conservamos el primero o puedes agregar una regla por fecha
    if not cvs.empty and "user" in cvs.columns:
        cvs = cvs.drop_duplicates(subset=["user"])

    usuarios_master = safe_merge(usuarios, cvs, left_on="_id", right_on="user", how="left")
    return usuarios_master


def generar_demo_postulantes() -> pd.DataFrame:
    """Genera un dataset de ejemplo para desarrollar o probar la plantilla sin MongoDB."""
    datos = [
        {
            "_id": "u01",
            "firstName": "Ana",
            "lastName": "García",
            "disponibilidad": "Inmediata",
            "modalidad": "Remoto",
            "location": "Lima, Perú",
            "rubros": ["Tecnología", "Data"],
            "profession": "Data Analyst",
            "createdAt": "2026-09-10",
        },
        {
            "_id": "u02",
            "firstName": "Luis",
            "lastName": "Mendoza",
            "disponibilidad": "15 días",
            "modalidad": "Híbrido",
            "location": "Bogotá, Colombia",
            "rubros": ["Finanzas"],
            "profession": "Data Engineer",
            "createdAt": "2026-09-18",
        },
        {
            "_id": "u03",
            "firstName": "Sofía",
            "lastName": "Rojas",
            "disponibilidad": "Inmediata",
            "modalidad": "Remoto",
            "location": "Santiago, Chile",
            "rubros": ["Tecnología", "Educación"],
            "profession": "Backend Developer",
            "createdAt": "2026-10-02",
        },
        {
            "_id": "u04",
            "firstName": "Carlos",
            "lastName": "Pérez",
            "disponibilidad": "30 días",
            "modalidad": "Presencial",
            "location": "Lima, Perú",
            "rubros": ["Logística"],
            "profession": "Data Analyst",
            "createdAt": "2026-10-14",
        },
        {
            "_id": "u05",
            "firstName": "Valeria",
            "lastName": "Torres",
            "disponibilidad": "Inmediata",
            "modalidad": "Híbrido",
            "location": "Ciudad de México, México",
            "rubros": ["Marketing", "E-commerce"],
            "profession": None,
            "createdAt": "2026-11-01",
        },
        {
            "_id": "u06",
            "firstName": "Diego",
            "lastName": "Castro",
            "disponibilidad": "15 días",
            "modalidad": "Remoto",
            "location": "Lima, Perú",
            "rubros": ["Tecnología"],
            "profession": "ML Engineer",
            "createdAt": "2026-11-12",
        },
    ]
    return pd.DataFrame(datos)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def cargar_postulantes(cache_path: Optional[str] = None) -> pd.DataFrame:
    """Lee el DataFrame de postulantes desde disco y lo cachea en memoria de Streamlit."""
    ruta = Path(cache_path) if cache_path else CACHE_PATH
    return load_df_cache(ruta, date_cols=["createdAt"])


def actualizar_cache_postulantes(
    usar_demo: bool = False,
    cache_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Reconstruye el caché en disco de Postulantes e invalida `@st.cache_data`."""
    ruta = cache_path or CACHE_PATH
    builder = generar_demo_postulantes if usar_demo else build_postulantes
    return refresh_module_cache(
        path=ruta,
        builder_fn=builder,
        clear_streamlit_cache_fn=cargar_postulantes.clear,
    )


def obtener_estado_cache_postulantes(cache_path: Optional[Path] = None) -> dict[str, Any]:
    """Devuelve metadatos del archivo de caché de Postulantes."""
    return get_cache_metadata(cache_path or CACHE_PATH, ttl_seconds=CACHE_TTL_SECONDS)
