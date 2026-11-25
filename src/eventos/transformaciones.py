"""Transformaciones y filtros puros para el dominio de Eventos."""

from __future__ import annotations

from typing import Optional, Sequence

import pandas as pd


def _texto_limpio(serie: pd.Series, default: str = "Sin especificar") -> pd.Series:
    """Normaliza valores nulos o vacíos en columnas de texto."""
    limpia = serie.fillna(default).astype(str).str.strip()
    return limpia.replace({"": default, "nan": default, "None": default})


def preparar_eventos(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza campos de eventos y calcula la tasa de asistencia por evento."""
    if df.empty:
        return df.copy()

    out = df.copy()

    titulo_base = out["title"] if "title" in out.columns else out.get(
        "name", pd.Series(dtype="object", index=out.index)
    )
    out["evento"] = _texto_limpio(titulo_base, default="Evento sin título")

    tipo_base = out["type"] if "type" in out.columns else out.get(
        "category", pd.Series(dtype="object", index=out.index)
    )
    out["tipo"] = _texto_limpio(tipo_base)
    out["modalidad"] = _texto_limpio(
        out.get("modality", pd.Series(dtype="object", index=out.index))
    )
    out["estado"] = _texto_limpio(
        out.get("status", pd.Series(dtype="object", index=out.index)),
        default="Programado",
    )

    fecha_base = out["startDate"] if "startDate" in out.columns else out.get(
        "date", pd.Series(pd.NaT, index=out.index)
    )
    out["fecha_evento"] = pd.to_datetime(fecha_base, errors="coerce")

    for col in ("inscritos", "asistentes"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(int)
        else:
            out[col] = 0

    out["tasa_asistencia_pct"] = (
        (out["asistentes"] / out["inscritos"].replace(0, pd.NA)) * 100
    ).fillna(0.0).round(1)

    return out


def filtrar_eventos(
    df: pd.DataFrame,
    tipos: Optional[Sequence[str]] = None,
    modalidades: Optional[Sequence[str]] = None,
    estados: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Aplica filtros seleccionados en el dashboard sobre el DataFrame de eventos."""
    if df.empty:
        return df.copy()

    mask = pd.Series(True, index=df.index)
    if tipos and "tipo" in df.columns:
        mask &= df["tipo"].isin(tipos)
    if modalidades and "modalidad" in df.columns:
        mask &= df["modalidad"].isin(modalidades)
    if estados and "estado" in df.columns:
        mask &= df["estado"].isin(estados)

    return df.loc[mask].copy()
