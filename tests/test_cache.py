"""Pruebas unitarias para el módulo de caché en disco (`cache.py`)."""

from pathlib import Path

import pandas as pd
import pytest

from cache import (
    CacheNotFoundError,
    get_cache_metadata,
    invalidate_cache_file,
    load_df_cache,
    load_or_build_df,
    refresh_module_cache,
    save_df_cache,
)


@pytest.mark.parametrize("ext", ["pkl", "parquet", "csv"])
def test_save_and_load_formats(tmp_path: Path, ext: str) -> None:
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "nombre": ["Ana", "Luis"],
            "createdAt": ["2026-10-01", "2026-10-02"],
        }
    )
    ruta = tmp_path / f"test_df.{ext}"

    save_df_cache(df, ruta)
    cargado = load_df_cache(ruta, date_cols=["createdAt"])

    assert ruta.exists()
    assert len(cargado) == 2
    assert pd.api.types.is_datetime64_any_dtype(cargado["createdAt"])


def test_load_missing_raises_cache_not_found(tmp_path: Path) -> None:
    with pytest.raises(CacheNotFoundError):
        load_df_cache(tmp_path / "inexistente.pkl")


def test_load_or_build_y_refresh_cache(tmp_path: Path) -> None:
    ruta = tmp_path / "modulo.pkl"
    llamadas = {"builder": 0, "cleared": 0}

    def builder() -> pd.DataFrame:
        llamadas["builder"] += 1
        return pd.DataFrame({"valor": [llamadas["builder"]]})

    def clear_fn() -> None:
        llamadas["cleared"] += 1

    # Primera carga construye y guarda en disco
    df1 = load_or_build_df(ruta, builder)
    assert df1["valor"].iloc[0] == 1
    assert llamadas["builder"] == 1

    # Segunda carga reutiliza el disco sin volver a llamar al builder
    df2 = load_or_build_df(ruta, builder, ttl_seconds=3600)
    assert df2["valor"].iloc[0] == 1
    assert llamadas["builder"] == 1

    # Refresco explícito reconstruye e invalida caché en memoria
    df3 = refresh_module_cache(ruta, builder, clear_streamlit_cache_fn=clear_fn)
    assert df3["valor"].iloc[0] == 2
    assert llamadas["cleared"] == 1

    meta = get_cache_metadata(ruta, ttl_seconds=3600)
    assert meta["existe"] is True
    assert meta["expirado"] is False
    assert meta["tamano_kb"] > 0

    assert invalidate_cache_file(ruta) is True
    assert invalidate_cache_file(ruta) is False
