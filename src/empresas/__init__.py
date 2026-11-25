"""Módulo de dominio: Empresas.

Expone únicamente las funciones públicas del módulo para mantener aislado
el trabajo del sub-equipo de Empresas en Git Flow.
"""

from src.empresas.cargar_datos import (
    actualizar_cache_empresas,
    build_empresas,
    cargar_empresas,
)

__all__ = [
    "actualizar_cache_empresas",
    "build_empresas",
    "cargar_empresas",
]
