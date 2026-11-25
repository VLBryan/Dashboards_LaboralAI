"""Transformaciones y filtros puros para el dominio de Postulantes.

Guía para el equipo de Data (Postulantes):
- Aquí van únicamente funciones puras `pd.DataFrame -> pd.DataFrame`.
- NO importes `streamlit` aquí: así cualquier transformación se puede probar
  fácilmente con `pytest` o reutilizar desde notebooks/scripts.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

import pandas as pd


def _extraer_ubicacion(valor: Any) -> str:
    """Normaliza el campo `location` ya venga como texto o diccionario de MongoDB."""
    if isinstance(valor, dict):
        partes = [valor.get("city"), valor.get("country")]
        texto = ", ".join(str(p).strip() for p in partes if p)
        return texto or "Sin especificar"
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "Sin especificar"
    texto = str(valor).strip()
    return texto or "Sin especificar"


def _limpiar_texto(serie: pd.Series, default: str = "Sin especificar") -> pd.Series:
    """Normaliza columnas de texto reemplazando vacíos y nulos de forma uniforme."""
    limpia = serie.fillna(default).astype(str).str.strip()
    return limpia.replace({"": default, "nan": default, "None": default})


def preparar_postulantes(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y enriquece el DataFrame maestro de postulantes.

    Columnas generadas/normalizadas:
    - `nombre_completo`: unión limpia de `firstName` y `lastName`.
    - `modalidad`, `disponibilidad`, `profession`: texto sin nulos.
    - `ubicacion`: texto unificado desde `location`.
    - `cantidad_rubros`: número de rubros asociados cuando `rubros` es lista.
    - `tiene_cv`: booleano indicando si posee profesión registrada.
    """
    if df.empty:
        return df.copy()

    out = df.copy()

    first_name = _limpiar_texto(out.get("firstName", pd.Series("", index=out.index)), "")
    last_name = _limpiar_texto(out.get("lastName", pd.Series("", index=out.index)), "")
    out["nombre_completo"] = (first_name + " " + last_name).str.strip().replace("", "Sin nombre")

    out["modalidad"] = _limpiar_texto(
        out.get("modalidad", pd.Series(dtype="object", index=out.index))
    )
    out["disponibilidad"] = _limpiar_texto(
        out.get("disponibilidad", pd.Series(dtype="object", index=out.index))
    )
    out["profession"] = _limpiar_texto(
        out.get("profession", pd.Series(dtype="object", index=out.index)),
        default="Sin profesión",
    )
    out["tiene_cv"] = out["profession"] != "Sin profesión"

    if "location" in out.columns:
        out["ubicacion"] = out["location"].map(_extraer_ubicacion)
    else:
        out["ubicacion"] = "Sin especificar"

    if "rubros" in out.columns:
        out["cantidad_rubros"] = out["rubros"].map(
            lambda x: len(x) if isinstance(x, (list, tuple, set)) else 0
        )
    else:
        out["cantidad_rubros"] = 0

    if "createdAt" in out.columns:
        out["createdAt"] = pd.to_datetime(out["createdAt"], errors="coerce")

    return out


def filtrar_postulantes(
    df: pd.DataFrame,
    modalidades: Optional[Sequence[str]] = None,
    disponibilidades: Optional[Sequence[str]] = None,
    profesiones: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Aplica filtros de dashboard sobre un DataFrame ya preparado."""
    if df.empty:
        return df.copy()

    mask = pd.Series(True, index=df.index)
    if modalidades and "modalidad" in df.columns:
        mask &= df["modalidad"].isin(modalidades)
    if disponibilidades and "disponibilidad" in df.columns:
        mask &= df["disponibilidad"].isin(disponibilidades)
    if profesiones and "profession" in df.columns:
        mask &= df["profession"].isin(profesiones)

    return df.loc[mask].copy()
