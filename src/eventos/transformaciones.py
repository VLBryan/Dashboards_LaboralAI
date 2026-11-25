"""Transformaciones y filtros puros para el dominio de Eventos.

Guía para el equipo de Data (Eventos):
- Coloca aquí funciones puras (`pd.DataFrame -> pd.DataFrame`) de limpieza,
  normalización de fechas y aplicación de filtros.
- Evita importar `streamlit` aquí para facilitar pruebas unitarias con `pytest`.
"""

from __future__ import annotations

import pandas as pd
