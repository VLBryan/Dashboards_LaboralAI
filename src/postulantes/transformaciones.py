"""Transformaciones y filtros puros para el dominio de Postulantes.

Guía para el equipo de Data (Postulantes):
- Escribe aquí funciones puras (`pd.DataFrame -> pd.DataFrame`) para limpiar nulos,
  parsear fechas, crear columnas derivadas y aplicar filtros del dashboard.
- Evita importar `streamlit` en este archivo para poder testearlo con `pytest`.

Ejemplo de estructura recomendada:
    def preparar_postulantes(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        ...
        return out
"""

from __future__ import annotations

import pandas as pd
