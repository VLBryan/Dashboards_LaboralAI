"""Módulo de dominio: Eventos.

Expone la API pública del módulo para `pages/3_Eventos.py` y el centro de
administración, manteniendo aislado el trabajo del sub-equipo de Eventos.
"""

from src.eventos.cargar_datos import (
    actualizar_cache_eventos,
    build_eventos,
    cargar_eventos,
    generar_demo_eventos,
    obtener_estado_cache_eventos,
)
from src.eventos.graficos import (
    grafico_asistencia_eventos,
    grafico_eventos_por_tipo,
)
from src.eventos.metricas import (
    calcular_kpis_eventos,
    resumen_eventos_por_tipo,
)
from src.eventos.transformaciones import (
    filtrar_eventos,
    preparar_eventos,
)

__all__ = [
    "actualizar_cache_eventos",
    "build_eventos",
    "cargar_eventos",
    "generar_demo_eventos",
    "obtener_estado_cache_eventos",
    "preparar_eventos",
    "filtrar_eventos",
    "calcular_kpis_eventos",
    "resumen_eventos_por_tipo",
    "grafico_asistencia_eventos",
    "grafico_eventos_por_tipo",
]
