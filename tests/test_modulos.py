"""Pruebas integradas de los módulos de dominio y renderizado Streamlit."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from streamlit.testing.v1 import AppTest

from src.empresas import (
    actualizar_cache_empresas,
    calcular_kpis_empresas,
    cargar_empresas,
    filtrar_empresas,
    grafico_empresas_por_sector,
    grafico_ofertas_por_tamano,
    preparar_empresas,
)
from src.eventos import (
    actualizar_cache_eventos,
    calcular_kpis_eventos,
    cargar_eventos,
    filtrar_eventos,
    grafico_asistencia_eventos,
    grafico_eventos_por_tipo,
    preparar_eventos,
)
from src.postulantes import (
    actualizar_cache_postulantes,
    calcular_kpis_postulantes,
    cargar_postulantes,
    filtrar_postulantes,
    grafico_postulantes_por_modalidad,
    grafico_top_profesiones,
    preparar_postulantes,
)


def test_flujo_completo_postulantes(tmp_path: Path) -> None:
    ruta = tmp_path / "postulantes.pkl"
    actualizar_cache_postulantes(usar_demo=True, cache_path=ruta)
    df = cargar_postulantes(cache_path=str(ruta))

    prep = preparar_postulantes(df)
    assert {"nombre_completo", "ubicacion", "cantidad_rubros", "tiene_cv"}.issubset(prep.columns)

    filtrado = filtrar_postulantes(prep, modalidades=["Remoto"])
    assert not filtrado.empty
    assert set(filtrado["modalidad"]) == {"Remoto"}

    kpis = calcular_kpis_postulantes(filtrado)
    assert kpis["total_postulantes"] == len(filtrado)

    assert isinstance(grafico_postulantes_por_modalidad(filtrado), go.Figure)
    assert isinstance(grafico_top_profesiones(filtrado), go.Figure)
    assert isinstance(grafico_postulantes_por_modalidad(pd.DataFrame()), go.Figure)


def test_flujo_completo_empresas(tmp_path: Path) -> None:
    ruta = tmp_path / "empresas.pkl"
    actualizar_cache_empresas(usar_demo=True, cache_path=ruta)
    df = cargar_empresas(cache_path=str(ruta))

    prep = preparar_empresas(df)
    filtrado = filtrar_empresas(prep, estados=["Activa"])
    assert not filtrado.empty
    assert set(filtrado["estado"]) == {"Activa"}

    kpis = calcular_kpis_empresas(filtrado)
    assert kpis["empresas_activas"] == len(filtrado)

    assert isinstance(grafico_empresas_por_sector(filtrado), go.Figure)
    assert isinstance(grafico_ofertas_por_tamano(filtrado), go.Figure)
    assert isinstance(grafico_empresas_por_sector(pd.DataFrame()), go.Figure)


def test_flujo_completo_eventos(tmp_path: Path) -> None:
    ruta = tmp_path / "eventos.pkl"
    actualizar_cache_eventos(usar_demo=True, cache_path=ruta)
    df = cargar_eventos(cache_path=str(ruta))

    prep = preparar_eventos(df)
    filtrado = filtrar_eventos(prep, tipos=["Workshop"])
    assert not filtrado.empty
    assert set(filtrado["tipo"]) == {"Workshop"}

    kpis = calcular_kpis_eventos(filtrado)
    assert kpis["total_eventos"] == len(filtrado)

    assert isinstance(grafico_eventos_por_tipo(filtrado), go.Figure)
    assert isinstance(grafico_asistencia_eventos(filtrado), go.Figure)
    assert isinstance(grafico_eventos_por_tipo(pd.DataFrame()), go.Figure)


ROOT_DIR = Path(__file__).resolve().parent.parent


def test_app_streamlit_navegacion_sin_errores() -> None:
    at = AppTest.from_file(str(ROOT_DIR / "app.py"))
    at.run()
    assert not at.exception


def test_paginas_renderizan_con_datos_demo(tmp_path: Path, monkeypatch) -> None:
    import src.empresas.cargar_datos as emp_cd
    import src.eventos.cargar_datos as ev_cd
    import src.postulantes.cargar_datos as post_cd

    ruta_post = tmp_path / "postulantes.pkl"
    ruta_emp = tmp_path / "empresas.pkl"
    ruta_ev = tmp_path / "eventos.pkl"

    monkeypatch.setattr(post_cd, "CACHE_PATH", ruta_post)
    monkeypatch.setattr(emp_cd, "CACHE_PATH", ruta_emp)
    monkeypatch.setattr(ev_cd, "CACHE_PATH", ruta_ev)

    actualizar_cache_postulantes(usar_demo=True, cache_path=ruta_post)
    actualizar_cache_empresas(usar_demo=True, cache_path=ruta_emp)
    actualizar_cache_eventos(usar_demo=True, cache_path=ruta_ev)

    for pagina in ("pages/1_Postulantes.py", "pages/2_Empresas.py", "pages/3_Eventos.py"):
        at = AppTest.from_file(str(ROOT_DIR / "app.py"))
        at.run()
        at.switch_page(pagina).run()
        assert not at.exception, f"Falló {pagina}: {at.exception}"
        assert len(at.metric) == 4

