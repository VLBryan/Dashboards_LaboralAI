"""Módulo de dominio: Postulantes.

Expone únicamente las funciones públicas del módulo para mantener aislado
el trabajo del sub-equipo de Postulantes en Git Flow.
"""

from src.postulantes.cargar_datos import (
    actualizar_cache_postulantes,
    build_postulantes,
    cargar_postulantes,
)

__all__ = [
    "actualizar_cache_postulantes",
    "build_postulantes",
    "cargar_postulantes",
]
