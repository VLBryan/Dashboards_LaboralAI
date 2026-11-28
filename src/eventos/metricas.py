import pandas as pd
import numpy as np


def calcular_kpis_eventos(df_events, df_inscripciones):
    datos = df_inscripciones
    return {
        "total_eventos": int(df_events["event_id"].nunique()) if not df_events.empty else 0,
        "total_inscripciones": int(datos["eventguest_id"].nunique()) if not datos.empty else 0,
        "participantes_unicos": int(datos["email_key"].nunique()) if not datos.empty else 0,
        "asistencias": int(datos["status"].eq("ATTENDED").sum()) if not datos.empty else 0,
        "eventos_con_inscripciones": int(datos["event_id"].nunique()) if not datos.empty else 0,
        "certificados_pagados": int(datos["certificado_pagado"].sum()) if "certificado_pagado" in datos.columns and not datos.empty else 0,
    }


def kpis_certificados(df_events, df_inscripciones):
    eventos_con_certificado = int(df_events["hasCertificate"].eq(True).sum()) if not df_events.empty else 0
    pagados = df_inscripciones[df_inscripciones["certificado_pagado"].fillna(False)].copy() if not df_inscripciones.empty else pd.DataFrame()
    sin_precio_valido = int(pagados["importe_certificado_estimado"].isna().sum()) if not pagados.empty else 0
    importe_total = pagados["importe_certificado_estimado"].sum(min_count=1) if not pagados.empty else np.nan
    if pd.isna(importe_total):
        importe_mostrado = "0,00" if pagados.empty else "No disponible"
    else:
        importe_mostrado = f"{importe_total:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return {
        "eventos_con_certificado": eventos_con_certificado,
        "certificados_pagados": int(pagados["eventguest_id"].nunique()) if not pagados.empty else 0,
        "importe_total": importe_total,
        "importe_mostrado": importe_mostrado,
        "sin_precio_valido": sin_precio_valido,
        "pagados_df": pagados,
    }


def hallazgos_clave(df_events, df_inscripciones, etiquetas):
    datos = df_inscripciones
    nombre_mejor = "Sin información"
    mayor_registro = 0
    if not datos.empty:
        ranking = datos.groupby("event_id")["eventguest_id"].nunique().sort_values(ascending=False)
        if not ranking.empty:
            mejor_id = ranking.index[0]
            mayor_registro = int(ranking.iloc[0])
            nombre_mejor = etiquetas.get(str(mejor_id), "Sin título")
    return {"nombre_mejor_evento": nombre_mejor, "mayor_registro_evento": mayor_registro}


def inscripciones_por_evento(df_inscripciones):
    if df_inscripciones.empty:
        return pd.DataFrame(columns=["event_id", "Inscripciones"])
    return df_inscripciones.groupby("event_id")["eventguest_id"].nunique().reset_index(name="Inscripciones")


def evolucion_inscripciones_mensual(df_inscripciones):
    if df_inscripciones.empty:
        return pd.DataFrame(columns=["Mes", "Inscripciones"])
    temporal = df_inscripciones.copy()
    temporal["registrationDate"] = pd.to_datetime(temporal["registrationDate"], errors="coerce", utc=True)
    temporal = temporal.dropna(subset=["registrationDate"])
    if temporal.empty:
        return pd.DataFrame(columns=["Mes", "Inscripciones"])
    temporal["Mes"] = temporal["registrationDate"].dt.strftime("%Y-%m")
    return temporal.groupby("Mes")["eventguest_id"].nunique().reset_index(name="Inscripciones").sort_values("Mes")


def estados_inscripcion(df_inscripciones):
    if df_inscripciones.empty:
        return pd.DataFrame(columns=["Estado", "Cantidad"])
    return df_inscripciones["status"].fillna("SIN INFORMACIÓN").value_counts().rename_axis("Estado").reset_index(name="Cantidad")


def eventos_por_modalidad(df_events):
    if df_events.empty:
        return pd.DataFrame(columns=["Modalidad", "Eventos"])
    return df_events["modality"].fillna("No informado").value_counts().rename_axis("Modalidad").reset_index(name="Eventos")


def inscripciones_por_categoria(df_inscripciones):
    if df_inscripciones.empty:
        return pd.DataFrame(columns=["category", "Inscripciones"])
    validos = df_inscripciones[df_inscripciones["category"].notna()].copy()
    if validos.empty:
        return pd.DataFrame(columns=["category", "Inscripciones"])
    return validos.groupby("category")["eventguest_id"].nunique().reset_index(name="Inscripciones").sort_values("Inscripciones", ascending=False)


def eventos_por_tipo(df_events):
    if df_events.empty:
        return pd.DataFrame(columns=["Tipo", "Eventos"])
    validos = df_events[df_events["type"].notna()]
    if validos.empty:
        return pd.DataFrame(columns=["Tipo", "Eventos"])
    return validos["type"].value_counts().rename_axis("Tipo").reset_index(name="Eventos")


def inscripciones_por_empresa(df_inscripciones):
    if df_inscripciones.empty:
        return pd.DataFrame(columns=["Empresa", "Inscripciones"])
    validos = df_inscripciones[df_inscripciones["companyId"].notna() | df_inscripciones["companyName"].notna()].copy()
    if validos.empty:
        return pd.DataFrame(columns=["Empresa", "Inscripciones"])
    validos["Empresa"] = validos["companyName"].fillna(validos["companyId"]).fillna("No informado")
    return validos.groupby("Empresa")["eventguest_id"].nunique().reset_index(name="Inscripciones").sort_values("Inscripciones", ascending=False)


def certificados_por_evento(df_inscripciones):
    if df_inscripciones.empty:
        return pd.DataFrame(columns=["event_id", "Certificados pagados"])
    pagados = df_inscripciones[df_inscripciones["certificado_pagado"].fillna(False)].copy()
    if pagados.empty:
        return pd.DataFrame(columns=["event_id", "Certificados pagados"])
    return pagados.groupby("event_id")["eventguest_id"].nunique().reset_index(name="Certificados pagados").sort_values("Certificados pagados", ascending=False)


def detalle_eventos(df_events, df_inscripciones):
    if df_events.empty:
        return pd.DataFrame()
    if df_inscripciones.empty:
        conteos = pd.DataFrame(columns=["event_id", "inscripciones", "participantes", "asistencias", "certificados"])
    else:
        conteos = df_inscripciones.groupby("event_id").agg(
            inscripciones=("eventguest_id", "nunique"),
            participantes=("email_key", "nunique"),
            asistencias=("status", lambda s: int(s.eq("ATTENDED").sum())),
            certificados=("certificado_pagado", "sum"),
        ).reset_index()
    tabla = df_events[[
        "event_id", "title", "date", "modality", "category", "type",
        "companyName", "registrationType", "hasCertificate", "certificatePrice",
    ]].merge(conteos, on="event_id", how="left", validate="one_to_one")
    for columna in ["inscripciones", "participantes", "asistencias", "certificados"]:
        tabla[columna] = tabla[columna].fillna(0).astype(int)
    tabla["Fecha"] = pd.to_datetime(tabla["date"], errors="coerce", utc=True).dt.strftime("%Y-%m-%d")
    return tabla


def participantes_creacion_cuenta(df_inscripciones, df_events):
    datos = df_inscripciones[df_inscripciones["email_key"].notna()].copy()
    if datos.empty:
        return pd.DataFrame()
    fechas_eventos = df_events[["event_id", "date"]].drop_duplicates("event_id").rename(columns={"date": "fecha_evento"})
    base = datos.merge(fechas_eventos, on="event_id", how="left", validate="many_to_one")
    base["registrationDate"] = pd.to_datetime(base["registrationDate"], errors="coerce", utc=True)
    base["fecha_evento"] = pd.to_datetime(base["fecha_evento"], errors="coerce", utc=True)
    base["fecha_cuenta"] = pd.to_datetime(base["fecha_creacion_usuario"], errors="coerce", utc=True)
    base = base.sort_values(["registrationDate", "fecha_evento"], kind="stable", na_position="last").drop_duplicates(subset="email_key", keep="first").copy()
    base["dia_evento"] = base["fecha_evento"].dt.normalize()
    base["dia_cuenta"] = base["fecha_cuenta"].dt.normalize()

    def clasificar(fila):
        if not bool(fila.get("cuenta_identificada", False)):
            return "Sin cuenta identificada"
        if pd.isna(fila["dia_evento"]) or pd.isna(fila["dia_cuenta"]):
            return "Sin fecha suficiente"
        if fila["dia_cuenta"] < fila["dia_evento"]:
            return "Antes del evento"
        if fila["dia_cuenta"] == fila["dia_evento"]:
            return "El mismo día del evento"
        return "Después del evento"

    base["momento_cuenta"] = base.apply(clasificar, axis=1)
    return base


def participantes_relacion_laboralai(df_inscripciones):
    datos = df_inscripciones[df_inscripciones["email_key"].notna()].copy()
    if datos.empty:
        return pd.Series(dtype=int)
    datos["registrationDate"] = pd.to_datetime(datos["registrationDate"], errors="coerce", utc=True)
    datos = datos.sort_values("registrationDate", na_position="first", kind="stable").drop_duplicates(subset="email_key", keep="last").copy()
    return datos["tipo_usuario"].fillna("No determinado").replace({"Sin cuenta identificada": "Sin cuenta registrada identificada"}).value_counts()
