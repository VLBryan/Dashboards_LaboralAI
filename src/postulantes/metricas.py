"""Cálculo de KPIs y tablas resumen para el dominio de Postulantes.

Guía para el equipo de Data (Postulantes):
- Coloca aquí las agregaciones y KPIs de negocio.
- Devuelve diccionarios o DataFrames pequeños listos para renderizar en `pages/1_Postulantes.py`.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def calcular_kpis_postulantes(df: pd.DataFrame) -> dict[str, Any]:
    """Calcula los indicadores principales (KPIs) del módulo de Postulantes."""
    if df.empty:
        return {
            "total_postulantes": 0,
            "con_cv": 0,
            "porcentaje_cv": 0.0,
            "profesiones_unicas": 0,
            "modalidad_principal": "N/A",
        }

    total = int(len(df))
    con_cv = int(df["tiene_cv"].sum()) if "tiene_cv" in df.columns else 0
    porcentaje_cv = round((con_cv / total) * 100, 1) if total > 0 else 0.0

    profesiones_validas = (
        df.loc[df["profession"] != "Sin profesión", "profession"].nunique()
        if "profession" in df.columns
        else 0
    )

    modalidad_principal = "N/A"
    if "modalidad" in df.columns and not df["modalidad"].dropna().empty:
        modalidad_principal = str(df["modalidad"].mode().iloc[0])

    return {
        "total_postulantes": total,
        "con_cv": con_cv,
        "porcentaje_cv": porcentaje_cv,
        "profesiones_unicas": int(profesiones_validas),
        "modalidad_principal": modalidad_principal,
    }


def resumen_por_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa los postulantes por modalidad de trabajo."""
    if df.empty or "modalidad" not in df.columns:
        return pd.DataFrame(columns=["modalidad", "cantidad"])

    resumen = (
        df.groupby("modalidad", dropna=False)
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )
    return resumen


def top_profesiones(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Obtiene el ranking de las profesiones más frecuentes entre postulantes."""
    if df.empty or "profession" not in df.columns:
        return pd.DataFrame(columns=["profession", "cantidad"])

    filtrado = df[df["profession"] != "Sin profesión"]
    if filtrado.empty:
        return pd.DataFrame(columns=["profession", "cantidad"])

    return (
        filtrado.groupby("profession")
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
        .head(top_n)
    )
