"""Cálculo de KPIs y tablas resumen para el dominio de Empresas.

Guía para el equipo de Data (Empresas):
- Define aquí métricas de negocio (retención, vacantes activas, conversión, etc.).
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def calcular_kpis_empresas(df: pd.DataFrame) -> dict[str, Any]:
    """Calcula KPIs principales de Empresas y sus ofertas publicadas."""
    if df.empty:
        return {
            "total_empresas": 0,
            "empresas_activas": 0,
            "ofertas_activas": 0,
            "promedio_ofertas": 0.0,
        }

    total = int(len(df))
    activas = int((df["estado"] == "Activa").sum()) if "estado" in df.columns else total
    ofertas_activas = int(df["ofertas_activas"].sum()) if "ofertas_activas" in df.columns else 0
    promedio_ofertas = round(ofertas_activas / total, 2) if total > 0 else 0.0

    return {
        "total_empresas": total,
        "empresas_activas": activas,
        "ofertas_activas": ofertas_activas,
        "promedio_ofertas": promedio_ofertas,
    }


def resumen_empresas_por_sector(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa cantidad de empresas y ofertas activas por sector."""
    if df.empty or "sector" not in df.columns:
        return pd.DataFrame(columns=["sector", "empresas", "ofertas_activas"])

    return (
        df.groupby("sector", dropna=False)
        .agg(
            empresas=("empresa", "count") if "empresa" in df.columns else ("sector", "count"),
            ofertas_activas=("ofertas_activas", "sum"),
        )
        .reset_index()
        .sort_values("empresas", ascending=False)
    )


def resumen_ofertas_por_tamano(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa ofertas activas y totales según el tamaño de empresa."""
    if df.empty or "tamano" not in df.columns:
        return pd.DataFrame(columns=["tamano", "ofertas_activas", "ofertas_totales"])

    return (
        df.groupby("tamano", dropna=False)
        .agg(
            ofertas_activas=("ofertas_activas", "sum"),
            ofertas_totales=("ofertas_totales", "sum"),
        )
        .reset_index()
        .sort_values("ofertas_activas", ascending=False)
    )
