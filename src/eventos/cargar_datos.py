import pandas as pd
import streamlit as st
from pymongo import MongoClient

from config import DB_NAME, MONGO_URI


CAMPOS_EVENTS = [
    "_id", "title", "date", "createdAt", "publishedAt", "isActive",
    "status", "modality", "spots", "isFree", "price", "organizer",
    "hasCertificate", "category", "type", "companyId", "companyName",
    "registrationType", "certificatePrice",
]

CAMPOS_GUESTS = [
    "_id", "event", "userEmail", "status", "registrationDate",
    "isCertificatePaid", "entityType", "entityRole", "discoveryInterest",
]

CAMPOS_USERS = [
    "_id", "email", "createdAt", "profession",
]


def normalizar_correo(serie):
    return serie.astype("string").str.strip().str.lower().replace("", pd.NA)


def normalizar_id(serie):
    return serie.astype("string").str.strip().replace("", pd.NA)


def normalizar_texto(serie, mayusculas=False):
    resultado = serie.astype("string").str.strip().replace("", pd.NA)
    if mayusculas:
        resultado = resultado.str.upper()
    return resultado


def normalizar_booleano(serie):
    texto = serie.astype("string").str.strip().str.lower()
    return texto.map({
        "true": True, "false": False, "1": True, "0": False,
        "yes": True, "no": False, "si": True, "sí": True,
    }).astype("boolean")


def normalizar_fecha(serie):
    return pd.to_datetime(serie, errors="coerce", utc=True)


def preparar_columnas(df, campos):
    return df.reindex(columns=campos)


def proyeccion(campos):
    return {campo: 1 for campo in campos}


@st.cache_data(ttl=600, show_spinner="Cargando eventos desde MongoDB...")
def cargar_eventos(db_name: str = DB_NAME, mongo_uri: str = MONGO_URI):
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    try:
        db = client[db_name]
        eventos = list(db["events"].find({}, proyeccion(CAMPOS_EVENTS)))
        invitados = list(db["eventguests"].find({}, proyeccion(CAMPOS_GUESTS)))
        usuarios = list(db["users"].find({}, proyeccion(CAMPOS_USERS)))
    finally:
        client.close()

    df_events = preparar_columnas(pd.DataFrame(eventos), CAMPOS_EVENTS)
    df_guests = preparar_columnas(pd.DataFrame(invitados), CAMPOS_GUESTS)
    df_users = preparar_columnas(pd.DataFrame(usuarios), CAMPOS_USERS)

    total_eventos_original = len(df_events)
    total_inscripciones_original = len(df_guests)

    if df_events.empty:
        raise ValueError("La colección events no contiene registros.")

    df_events = df_events.rename(columns={"_id": "event_id"})
    df_guests = df_guests.rename(columns={"_id": "eventguest_id"})

    df_events["event_id"] = normalizar_id(df_events["event_id"])
    df_guests["event_id"] = normalizar_id(df_guests["event"])
    df_guests["eventguest_id"] = normalizar_id(df_guests["eventguest_id"])

    if df_events["event_id"].isna().any():
        raise ValueError("Hay eventos sin identificador.")
    if df_events["event_id"].duplicated().any():
        raise ValueError("Hay identificadores duplicados en events.")
    if df_guests["eventguest_id"].isna().any():
        raise ValueError("Hay inscripciones sin identificador.")
    if df_guests["eventguest_id"].duplicated().any():
        raise ValueError("Hay identificadores duplicados en eventguests.")

    for columna in ["date", "createdAt", "publishedAt"]:
        df_events[columna] = normalizar_fecha(df_events[columna])

    textos_eventos = [
        "title", "status", "modality", "organizer", "category", "type",
        "companyId", "companyName", "registrationType",
    ]
    for columna in textos_eventos:
        df_events[columna] = normalizar_texto(df_events[columna])

    df_events["companyId"] = normalizar_id(df_events["companyId"])
    df_events["status"] = normalizar_texto(df_events["status"], mayusculas=True)
    df_events["modality"] = df_events["modality"].str.lower().replace({
        "presencial": "Presencial", "virtual": "Virtual",
        "híbrido": "Híbrido", "hibrido": "Híbrido",
    })

    for columna in ["isActive", "isFree", "hasCertificate"]:
        df_events[columna] = normalizar_booleano(df_events[columna])
    for columna in ["spots", "price", "certificatePrice"]:
        df_events[columna] = pd.to_numeric(df_events[columna], errors="coerce")

    df_events["categoria_dashboard"] = df_events["category"].fillna("No informado")
    df_events["tipo_evento_dashboard"] = df_events["type"].fillna("No informado")
    df_events["empresa_dashboard"] = df_events["companyName"].fillna("No informado")
    df_events["registro_dashboard"] = df_events["registrationType"].fillna("No informado")

    df_guests["registrationDate"] = normalizar_fecha(df_guests["registrationDate"])
    df_guests["email_key"] = normalizar_correo(df_guests["userEmail"])
    df_guests["status"] = normalizar_texto(df_guests["status"], mayusculas=True).fillna("SIN INFORMACIÓN")
    df_guests["isCertificatePaid"] = normalizar_booleano(df_guests["isCertificatePaid"])

    for columna in ["entityType", "entityRole", "discoveryInterest"]:
        df_guests[columna] = normalizar_texto(df_guests[columna])
        df_guests[f"{columna}_dashboard"] = df_guests[columna].fillna("No informado")

    df_users["email_key"] = normalizar_correo(df_users["email"])
    df_users["createdAt"] = normalizar_fecha(df_users["createdAt"])
    df_users["profession"] = normalizar_texto(df_users["profession"])
    df_users = df_users.rename(columns={"createdAt": "fecha_creacion_usuario"})
    df_users = df_users.dropna(subset=["email_key"]).copy()
    df_users = df_users.sort_values("fecha_creacion_usuario", na_position="last", kind="stable").drop_duplicates(subset=["email_key"], keep="first")

    usuarios_cruce = df_users[["email_key", "fecha_creacion_usuario", "profession"]].copy()
    invitados_con_correo = df_guests[df_guests["email_key"].notna()].copy()
    invitados_sin_correo = df_guests[df_guests["email_key"].isna()].copy()

    inscritos_con_correo = invitados_con_correo.merge(
        usuarios_cruce, on="email_key", how="left", validate="many_to_one", indicator=True
    )
    inscritos_con_correo["cuenta_identificada"] = inscritos_con_correo["_merge"].eq("both")
    inscritos_con_correo = inscritos_con_correo.drop(columns=["_merge"])

    invitados_sin_correo["fecha_creacion_usuario"] = pd.NaT
    invitados_sin_correo["profession"] = pd.NA
    invitados_sin_correo["cuenta_identificada"] = False

    df_inscripciones = pd.concat([inscritos_con_correo, invitados_sin_correo], ignore_index=True)
    df_inscripciones["profesion_dashboard"] = normalizar_texto(df_inscripciones["profession"]).fillna("No informado")

    def clasificar_usuario(fila):
        if pd.isna(fila["email_key"]):
            return "No determinado"
        if not fila["cuenta_identificada"]:
            return "Sin cuenta identificada"
        fecha_cuenta = fila["fecha_creacion_usuario"]
        fecha_registro = fila["registrationDate"]
        if pd.isna(fecha_cuenta) or pd.isna(fecha_registro):
            return "No determinado"
        if fecha_cuenta <= fecha_registro:
            return "Usuario Laboral.AI"
        return "Cuenta creada después"

    df_inscripciones["tipo_usuario"] = df_inscripciones.apply(clasificar_usuario, axis=1)

    campos_evento_para_cruce = [
        "event_id", "title", "date", "modality", "category", "type",
        "companyId", "companyName", "registrationType", "certificatePrice",
        "isFree", "hasCertificate", "price", "categoria_dashboard",
        "tipo_evento_dashboard", "empresa_dashboard", "registro_dashboard",
    ]
    df_inscripciones = df_inscripciones.merge(
        df_events[campos_evento_para_cruce], on="event_id", how="left",
        validate="many_to_one", indicator=True
    )
    df_inscripciones["evento_identificado"] = df_inscripciones["_merge"].eq("both")
    df_inscripciones = df_inscripciones.drop(columns=["_merge"])

    df_inscripciones["certificado_pagado"] = df_inscripciones["isCertificatePaid"].eq(True).fillna(False).astype(bool)
    precio_valido = df_inscripciones["certificatePrice"].notna() & df_inscripciones["certificatePrice"].ge(0)
    condicion_importe = df_inscripciones["certificado_pagado"] & precio_valido & df_inscripciones["evento_identificado"]
    df_inscripciones["importe_certificado_estimado"] = df_inscripciones["certificatePrice"].where(condicion_importe)

    if len(df_events) != total_eventos_original:
        raise ValueError("Cambió el número de eventos tras la limpieza.")
    if len(df_inscripciones) != total_inscripciones_original:
        raise ValueError("El cruce alteró el número de inscripciones.")
    if df_inscripciones["eventguest_id"].duplicated().any():
        raise ValueError("El cruce generó inscripciones duplicadas.")

    return df_events, df_inscripciones
