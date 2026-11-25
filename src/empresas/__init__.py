"""Módulo de dominio: Empresas.

Expone la API pública del módulo para `pages/2_Empresas.py` y el centro de
administración, manteniendo aislado el trabajo del sub-equipo de Empresas.
"""

from src.empresas.cargar_datos import (
    actualizar_cache_empresas,
    build_empresas,
    cargar_empresas,
    generar_demo_empresas,
    obtener_estado_cache_empresas,
)
from src.empresas.graficos import (
    grafico_empresas_por_sector,
    grafico_ofertas_por_tamano,
)
from src.empresas.metricas import (
    calcular_kpis_empresas,
    resumen_empresas_por_sector,
    resumen_ofertas_por_tamano,
)
from src.empresas.transformaciones import (
    filtrar_empresas,
    preparar_empresas,
)

__all__ = [
    "actualizar_cache_empresas",
    "build_empresas",
    "cargar_empresas",
    "generar_demo_empresas",
    "obtener_estado_cache_empresas",
    "preparar_empresas",
    "filtrar_empresas",
    "calcular_kpis_empresas",
    "resumen_empresas_por_sector",
    "resumen_ofertas_por_tamano",
    "grafico_empresas_por_sector",
    "grafico_ofertas_por_tamano",
]
