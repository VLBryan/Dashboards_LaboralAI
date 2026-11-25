"""Pruebas de los módulos de dominio y despliegue limpio de páginas Streamlit."""

from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

import src.empresas.cargar_datos as emp_cd
import src.eventos.cargar_datos as ev_cd
import src.postulantes.cargar_datos as post_cd

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_cache_memoria_por_modulo(monkeypatch) -> None:
    contadores = {"post": 0, "emp": 0, "ev": 0}

    def fake_build_post(db_name: str = "test") -> pd.DataFrame:
        contadores["post"] += 1
        return pd.DataFrame({"_id": ["u1"], "origen": [contadores["post"]]})

    def fake_build_emp(db_name: str = "test") -> pd.DataFrame:
        contadores["emp"] += 1
        return pd.DataFrame({"_id": ["e1"], "origen": [contadores["emp"]]})

    def fake_build_ev(db_name: str = "test") -> pd.DataFrame:
        contadores["ev"] += 1
        return pd.DataFrame({"_id": ["ev1"], "origen": [contadores["ev"]]})

    monkeypatch.setattr(post_cd, "build_postulantes", fake_build_post)
    monkeypatch.setattr(emp_cd, "build_empresas", fake_build_emp)
    monkeypatch.setattr(ev_cd, "build_eventos", fake_build_ev)

    post_cd.actualizar_cache_postulantes()
    emp_cd.actualizar_cache_empresas()
    ev_cd.actualizar_cache_eventos()

    # Primera llamada consulta y cachea en memoria; segunda reutiliza RAM
    assert post_cd.cargar_postulantes()["origen"].iloc[0] == 1
    assert post_cd.cargar_postulantes()["origen"].iloc[0] == 1
    assert contadores["post"] == 1

    assert emp_cd.cargar_empresas()["origen"].iloc[0] == 1
    assert emp_cd.cargar_empresas()["origen"].iloc[0] == 1
    assert contadores["emp"] == 1

    assert ev_cd.cargar_eventos()["origen"].iloc[0] == 1
    assert ev_cd.cargar_eventos()["origen"].iloc[0] == 1
    assert contadores["ev"] == 1

    # Al invalidar caché en memoria, la siguiente lectura vuelve a construir
    post_cd.actualizar_cache_postulantes()
    assert post_cd.cargar_postulantes()["origen"].iloc[0] == 2
    assert contadores["post"] == 2


def test_app_y_paginas_en_blanco_despliegan_sin_errores() -> None:
    at_inicio = AppTest.from_file(str(ROOT_DIR / "app.py"))
    at_inicio.run()
    assert not at_inicio.exception

    for pagina in ("pages/1_Postulantes.py", "pages/2_Empresas.py", "pages/3_Eventos.py"):
        at = AppTest.from_file(str(ROOT_DIR / "app.py"))
        at.run()
        at.switch_page(pagina).run()
        assert not at.exception, f"Falló {pagina}: {at.exception}"
        assert len(at.title) == 1
        assert len(at.metric) == 0
