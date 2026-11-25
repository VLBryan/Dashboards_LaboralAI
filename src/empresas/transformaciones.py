"""Transformaciones y filtros puros para el dominio de Empresas.

Guía para el equipo de Data (Empresas):
- Mantén todas las reglas de limpieza y normalización aquí (sin importar Streamlit).
"""

from __future__ import annotations

from typing import Optional, Sequence

import pandas as pd


def _texto_limpio(serie: pd.Series, default: str = "Sin especificar") -> pd.Series:
    """Normaliza cadenas nulas o vacías de forma segura."""
    limpia = serie.fillna(default).astype(str).str.strip()
    return limpia.replace({"": default, "nan": default, "None": default})


def preparar_empresas(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas clave de empresas, conteos de ofertas y estado."""
    if df.empty:
        return df.copy()

    out = df.copy()
    out["empresa"] = _texto_limpio(
        out.get("name", pd.Series(dtype="object", index=out.index)),
        default="Empresa sin nombre",
    )

    sector_base = out["sector"] if "sector" in out.columns else out.get(
        "industry", pd.Series(dtype="object", index=out.index)
    )
    out["sector"] = _texto_limpio(sector_base)
    out["tamano"] = _texto_limpio(
        out.get("size", pd.Series(dtype="object", index=out.index))
    )
    out["pais"] = _texto_limpio(
        out.get("country", pd.Series(dtype="object", index=out.index))
    )

    if "isActive" in out.columns:
        out["estado"] = out["isActive"].fillna(False).astype(bool).map(
            lambda activo: "Activa" if activo else "Inactiva"
        )
    else:
        out["estado"] = "Activa"

    for col in ("ofertas_totales", "ofertas_activas"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(int)
        else:
            out[col] = 0

    if "createdAt" in out.columns:
        out["createdAt"] = pd.to_datetime(out["createdAt"], errors="coerce")

    return out


def filtrar_empresas(
    df: pd.DataFrame,
    sectores: Optional[Sequence[str]] = None,
    tamanos: Optional[Sequence[str]] = None,
    estados: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Filtra el DataFrame preparado de empresas según selecciones del dashboard."""
    if df.empty:
        return df.copy()

    mask = pd.Series(True, index=df.index)
    if sectores and "sector" in df.columns:
        mask &= df["sector"].isin(sectores)
    if tamanos and "tamano" in df.columns:
        mask &= df["tamano"].isin(tamanos)
    if estados and "estado" in df.columns:
        mask &= df["estado"].isin(estados)

    return df.loc[mask].copy()
