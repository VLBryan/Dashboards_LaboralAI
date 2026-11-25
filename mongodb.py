"""Utilidades compartidas de conexión y extracción segura desde MongoDB.

Guía para el equipo de Data:
- Usa `get_mongo_client()` para abrir una conexión con timeout controlado.
- Usa `get_collection_df()` para convertir colecciones a DataFrames normalizados
  (convierte automáticamente `ObjectId` a `str` para evitar errores en merges y UI).
- Usa `safe_merge()` para unir colecciones sin que falle si alguna viene vacía.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

import pandas as pd
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import DB_NAME, MONGO_TIMEOUT_MS, MONGO_URI


class MongoConnectionError(RuntimeError):
    """Error controlado cuando no es posible conectarse o consultar MongoDB."""


def get_mongo_client(
    uri: Optional[str] = None,
    timeout_ms: int = MONGO_TIMEOUT_MS,
) -> MongoClient:
    """Crea un cliente de MongoDB con timeout de selección de servidor.

    Parámetros:
        uri: Cadena de conexión. Si es None, usa `config.MONGO_URI`.
        timeout_ms: Tiempo máximo de espera en milisegundos para conectar.
    """
    resolved_uri = uri or MONGO_URI
    return MongoClient(resolved_uri, serverSelectionTimeoutMS=timeout_ms)


def _convert_value_if_objectid(value: Any) -> Any:
    """Convierte ObjectId individuales o listas de ObjectId a string."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, list):
        return [str(v) if isinstance(v, ObjectId) else v for v in value]
    return value


def _contains_objectid(value: Any) -> bool:
    """Detecta si un valor es un ObjectId o una lista que contiene ObjectId."""
    if isinstance(value, ObjectId):
        return True
    if isinstance(value, list):
        return any(isinstance(item, ObjectId) for item in value)
    return False


def normalizar_object_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte columnas que contienen `bson.ObjectId` a `str`.

    Esto evita errores al hacer `pd.merge()` entre colecciones donde un ID
    puede venir como `ObjectId` o `str`, y evita fallos de serialización en Streamlit.
    """
    if df.empty:
        return df

    df_clean = df.copy()
    for col in df_clean.columns:
        if df_clean[col].dtype == "object":
            sample = df_clean[col].dropna()
            if not sample.empty and sample.map(_contains_objectid).any():
                df_clean[col] = df_clean[col].map(_convert_value_if_objectid)
    return df_clean


def get_collection_df(
    client: MongoClient,
    db_name: str = DB_NAME,
    coll_name: str = "",
    query: Optional[Mapping[str, Any]] = None,
    projection: Optional[Mapping[str, Any]] = None,
    convert_object_ids: bool = True,
) -> pd.DataFrame:
    """Consulta una colección de MongoDB y devuelve un DataFrame limpio.

    Parámetros:
        client: Instancia activa de `MongoClient`.
        db_name: Nombre de la base de datos.
        coll_name: Nombre de la colección.
        query: Filtro MongoDB (ej. `{"isActive": True}`).
        projection: Campos a incluir/excluir (ej. `{"firstName": 1}`).
        convert_object_ids: Si es True, convierte campos `ObjectId` a `str`.
    """
    if not coll_name:
        raise ValueError("Debes especificar `coll_name` para consultar MongoDB.")

    try:
        db = client[db_name]
        cursor = db[coll_name].find(query or {}, projection)
        docs = list(cursor)
    except PyMongoError as exc:
        raise MongoConnectionError(
            f"Error al consultar '{db_name}.{coll_name}' en MongoDB: {exc}"
        ) from exc

    if not docs:
        return pd.DataFrame()

    df = pd.DataFrame(docs)
    return normalizar_object_ids(df) if convert_object_ids else df


def safe_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_on: str,
    right_on: str,
    how: str = "left",
    suffixes: tuple[str, str] = ("", "_dup"),
) -> pd.DataFrame:
    """Realiza un merge tolerante a DataFrames vacíos o claves faltantes.

    Útil en pipelines de MongoDB donde una colección secundaria aún no tiene
    documentos o el filtro devolvió cero filas.
    """
    if left.empty:
        return left.copy()
    if right.empty or left_on not in left.columns or right_on not in right.columns:
        return left.copy()
    return left.merge(
        right,
        left_on=left_on,
        right_on=right_on,
        how=how,
        suffixes=suffixes,
    )
