"""Cálculo de KPIs y resúmenes agregados para el dominio de Eventos."""

from __future__ import annotations

from typing import Any

import pandas as pd


def calcular_kpis_eventos(df: pd.DataFrame) -> dict[str, Any]:
    """Calcula KPIs de volumen y asistencia del módulo de Eventos."""
    if df.empty:
        return {
            "total_eventos": 0,
            "total_inscritos": 0,
            "total_asistentes": 0,
            "tasa_asistencia_global": 0.0,
        }

    total_eventos = int(len(df))
    total_inscritos = int(df["inscritos"].sum()) if "inscritos" in df.columns else 0
    total_asistentes = int(df["asistentes"].sum()) if "asistentes" in df.columns else 0
    tasa_global = (
        round((total_asistentes / total_inscritos) * 100, 1)
        if total_inscritos > 0
        else 0.0
    )

    return {
        "total_eventos": total_eventos,
        "total_inscritos": total_inscritos,
        "total_asistentes": total_asistentes,
        "tasa_asistencia_global": tasa_global,
    }


def resumen_eventos_por_tipo(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa cantidad de eventos, inscritos y asistentes por tipo."""
    if df.empty or "tipo" not in df.columns:
        return pd.DataFrame(columns=["tipo", "eventos", "inscritos", "asistentes"])

    return (
        df.groupby("tipo", dropna=False)
        .agg(
            eventos=("evento", "count") if "evento" in df.columns else ("tipo", "count"),
            inscritos=("inscritos", "sum"),
            asistentes=("asistentes", "sum"),
        )
        .reset_index()
        .sort_values("inscritos", ascending=False)
    )
