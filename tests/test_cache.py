"""Pruebas unitarias para la gestión de caché en memoria (`cache.py`)."""

import pandas as pd
import streamlit as st

from cache import invalidar_cache_modulo


def test_cache_en_memoria_e_invalidacion() -> None:
    ejecuciones = {"count": 0}

    @st.cache_data(ttl=3600, show_spinner=False)
    def cargar_ejemplo() -> pd.DataFrame:
        ejecuciones["count"] += 1
        return pd.DataFrame({"llamada": [ejecuciones["count"]]})

    df1 = cargar_ejemplo()
    df2 = cargar_ejemplo()
    assert df1["llamada"].iloc[0] == 1
    assert df2["llamada"].iloc[0] == 1
    assert ejecuciones["count"] == 1

    invalidar_cache_modulo(cargar_ejemplo, modulo="ejemplo")

    df3 = cargar_ejemplo()
    assert df3["llamada"].iloc[0] == 2
    assert ejecuciones["count"] == 2
