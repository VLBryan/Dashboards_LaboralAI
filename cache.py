"""Gestión centralizada de caché en disco para DataFrames.

Arquitectura de caché en dos niveles usada en la plantilla:
1. Disco (`cache/<modulo>.pkl` o `.parquet` / `.csv`): persiste la extracción de
   MongoDB entre reinicios de Streamlit para no saturar la base de datos.
2. Memoria (`@st.cache_data` en cada `src/<modulo>/cargar_datos.py`): evita releer
   el disco en cada interacción del usuario dentro de la misma sesión/servidor.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Callable, Optional, Sequence, Union

import pandas as pd

PathLike = Union[str, Path]


class CacheNotFoundError(FileNotFoundError):
    """Se lanza cuando el archivo de caché en disco aún no ha sido generado."""


def _resolve_format(path: Path, fmt: Optional[str] = None) -> str:
    """Determina el formato de archivo a partir del parámetro o extensión."""
    resolved = (fmt or path.suffix.lstrip(".") or "pkl").lower()
    if resolved == "pickle":
        resolved = "pkl"
    if resolved not in {"pkl", "parquet", "csv"}:
        raise ValueError(
            f"Formato de caché no soportado: '{resolved}'. Usa 'pkl', 'parquet' o 'csv'."
        )
    return resolved


def save_df_cache(
    df: pd.DataFrame,
    path: PathLike,
    fmt: Optional[str] = None,
) -> Path:
    """Guarda un DataFrame en disco creando las carpetas necesarias.

    Parámetros:
        df: DataFrame a persistir.
        path: Ruta destino (ej. `cache/postulantes.pkl`).
        fmt: Formato opcional (`pkl`, `parquet`, `csv`). Si es None, se deduce de la extensión.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    resolved_fmt = _resolve_format(target, fmt)

    if resolved_fmt == "pkl":
        df.to_pickle(target)
    elif resolved_fmt == "parquet":
        df.to_parquet(target, index=False)
    else:
        df.to_csv(target, index=False)

    return target


def load_df_cache(
    path: PathLike,
    date_cols: Optional[Sequence[str]] = None,
    fmt: Optional[str] = None,
) -> pd.DataFrame:
    """Carga un DataFrame desde el caché en disco.

    Parámetros:
        path: Ruta del archivo de caché.
        date_cols: Columnas opcionales a convertir con `pd.to_datetime` si existen.
        fmt: Formato opcional (`pkl`, `parquet`, `csv`).
    """
    target = Path(path)
    if not target.exists():
        raise CacheNotFoundError(
            f"No existe el archivo de caché '{target}'. "
            "Genera o actualiza el caché primero."
        )

    resolved_fmt = _resolve_format(target, fmt)
    if resolved_fmt == "pkl":
        df = pd.read_pickle(target)
    elif resolved_fmt == "parquet":
        df = pd.read_parquet(target)
    else:
        df = pd.read_csv(target, index_col=False)

    if date_cols:
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def invalidate_cache_file(path: PathLike) -> bool:
    """Elimina un archivo de caché en disco si existe. Retorna True si fue borrado."""
    target = Path(path)
    if target.exists():
        os.remove(target)
        return True
    return False


def get_cache_metadata(
    path: PathLike,
    ttl_seconds: Optional[int] = None,
) -> dict[str, Any]:
    """Devuelve información de estado del caché en disco para mostrar en la UI."""
    target = Path(path)
    if not target.exists():
        return {
            "existe": False,
            "ruta": str(target),
            "actualizado_en": None,
            "antiguedad_seg": None,
            "expirado": True,
            "tamano_kb": 0.0,
        }

    stat = target.stat()
    updated_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).astimezone()
    age_seconds = max(0.0, (datetime.now().astimezone() - updated_at).total_seconds())
    expired = bool(ttl_seconds is not None and age_seconds > ttl_seconds)

    return {
        "existe": True,
        "ruta": str(target),
        "actualizado_en": updated_at,
        "antiguedad_seg": round(age_seconds, 1),
        "expirado": expired,
        "tamano_kb": round(stat.st_size / 1024, 2),
    }


def load_or_build_df(
    path: PathLike,
    builder_fn: Callable[[], pd.DataFrame],
    date_cols: Optional[Sequence[str]] = None,
    force_refresh: bool = False,
    ttl_seconds: Optional[int] = None,
) -> pd.DataFrame:
    """Carga un DataFrame desde disco o lo construye y persiste si falta o expiró.

    Centraliza el flujo de caché para que todos los módulos (`postulantes`,
    `empresas`, `eventos`) compartan la misma lógica sin duplicar código.
    """
    target = Path(path)
    meta = get_cache_metadata(target, ttl_seconds=ttl_seconds)

    if not force_refresh and meta["existe"] and not meta["expirado"]:
        return load_df_cache(target, date_cols=date_cols)

    df = builder_fn()
    save_df_cache(df, target)
    return df


def refresh_module_cache(
    path: PathLike,
    builder_fn: Callable[[], pd.DataFrame],
    clear_streamlit_cache_fn: Optional[Callable[[], None]] = None,
) -> pd.DataFrame:
    """Reconstruye el DataFrame, lo persiste en disco e invalida `@st.cache_data`.

    Evita duplicar la lógica de refresco en cada `src/<modulo>/cargar_datos.py`.
    """
    df = builder_fn()
    save_df_cache(df, path)
    if clear_streamlit_cache_fn is not None:
        clear_streamlit_cache_fn()
    return df

