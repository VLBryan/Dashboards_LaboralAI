import pandas as pd


def filtrar_por_fecha(df_events, rango):
    eventos = df_events.copy()
    if isinstance(rango, (tuple, list)) and len(rango) == 2:
        fecha_inicio, fecha_fin = rango
        fechas = pd.to_datetime(eventos["date"], errors="coerce", utc=True).dt.date
        eventos = eventos[fechas.between(fecha_inicio, fecha_fin)]
    return eventos


def filtrar_por_evento(df_events, evento):
    if evento and evento != "Todos":
        return df_events[df_events["event_id"].astype(str) == str(evento)].copy()
    return df_events.copy()


def filtrar_por_modalidad(df_events, modalidad):
    if modalidad and modalidad != "Todas":
        return df_events[df_events["modality"].astype(str) == str(modalidad)].copy()
    return df_events.copy()


def filtrar_por_empresa(df_events, empresa):
    if not empresa or empresa == "Todas":
        return df_events.copy()
    nombres_empresa = df_events["companyName"].fillna(df_events["companyId"]).astype("string").str.strip()
    return df_events[nombres_empresa.eq(empresa).fillna(False)].copy()


def filtrar_por_categoria(df_events, categoria):
    if not categoria or categoria == "Todas":
        return df_events.copy()
    categorias = df_events["category"].astype("string").str.strip()
    return df_events[categorias.eq(categoria).fillna(False)].copy()


def aplicar_filtros_eventos(df_events, rango=None, evento="Todos", modalidad="Todas",
                            empresa="Todas", categoria="Todas"):
    df = filtrar_por_fecha(df_events, rango)
    df = filtrar_por_evento(df, evento)
    df = filtrar_por_modalidad(df, modalidad)
    df = filtrar_por_empresa(df, empresa)
    df = filtrar_por_categoria(df, categoria)
    return df


def filtrar_inscripciones_por_eventos(df_inscripciones, df_events_filtrados):
    if df_events_filtrados.empty:
        return df_inscripciones.iloc[0:0].copy()
    return df_inscripciones[df_inscripciones["event_id"].isin(df_events_filtrados["event_id"])].copy()


def etiquetas_eventos(df_events):
    return {str(row["event_id"]): (row.get("title") or "Sin título") for _, row in df_events.iterrows()}


def nombre_evento_desde_id(etiquetas, event_id):
    return etiquetas.get(str(event_id), "Sin título")


def obtener_mes_mayor_actividad(datos):
    if datos is None or datos.empty:
        return "Sin datos", 0
    temporal = datos.copy()
    temporal["registrationDate"] = pd.to_datetime(temporal["registrationDate"], errors="coerce", utc=True)
    temporal = temporal.dropna(subset=["registrationDate"])
    if temporal.empty:
        return "Sin datos", 0
    temporal["Mes"] = temporal["registrationDate"].dt.strftime("%Y-%m")
    mensual = temporal.groupby("Mes")["eventguest_id"].nunique().sort_values(ascending=False)
    if mensual.empty:
        return "Sin datos", 0
    mes = mensual.index[0]
    try:
        ts = pd.to_datetime(mes + "-01")
        nombre = f"{ts.strftime('%B')} {ts.year}"
        meses_en = {
            "January": "Enero", "February": "Febrero", "March": "Marzo",
            "April": "Abril", "May": "Mayo", "June": "Junio",
            "July": "Julio", "August": "Agosto", "September": "Septiembre",
            "October": "Octubre", "November": "Noviembre", "December": "Diciembre",
        }
        for en, es in meses_en.items():
            nombre = nombre.replace(en, es)
    except Exception:
        nombre = mes
    return nombre, int(mensual.iloc[0])
