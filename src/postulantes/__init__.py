"""Módulo de dominio: Postulantes.

Expone la API pública del módulo para que `pages/1_Postulantes.py` y el centro
de administración importen solo lo necesario sin acoplarse a la estructura interna.
"""

from src.postulantes.cargar_datos import (
    actualizar_cache_postulantes,
    build_postulantes,
    cargar_postulantes,
    generar_demo_postulantes,
    obtener_estado_cache_postulantes,
)
from src.postulantes.graficos import (
    grafico_postulantes_por_modalidad,
    grafico_top_profesiones,
)
from src.postulantes.metricas import (
    calcular_kpis_postulantes,
    resumen_por_modalidad,
    top_profesiones,
)
from src.postulantes.transformaciones import (
    filtrar_postulantes,
    preparar_postulantes,
)

__all__ = [
    "actualizar_cache_postulantes",
    "build_postulantes",
    "cargar_postulantes",
    "generar_demo_postulantes",
    "obtener_estado_cache_postulantes",
    "preparar_postulantes",
    "filtrar_postulantes",
    "calcular_kpis_postulantes",
    "resumen_por_modalidad",
    "top_profesiones",
    "grafico_postulantes_por_modalidad",
    "grafico_top_profesiones",
]
