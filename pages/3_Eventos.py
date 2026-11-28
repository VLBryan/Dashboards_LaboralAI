import streamlit as st
import pandas as pd

from config import DB_NAME, MONGO_URI
from src.eventos.cargar_datos import cargar_eventos
from src.eventos import transformaciones as T
from src.eventos import metricas as M
from src.eventos import graficos as G


st.set_page_config(page_title="Eventos | Laboral.AI", page_icon="📅", layout="wide", initial_sidebar_state="expanded")


def titulo_seccion(texto):
    st.markdown(f"### {texto}")


def sin_datos(mensaje):
    st.info(mensaje)


def grafico(fig, height=None):
    if fig is None:
        sin_datos("Sin datos para mostrar.")
        return
    if height is not None:
        fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True)


def numero(valor):
    try:
        return f"{int(valor):,}".replace(",", ".")
    except Exception:
        return str(valor)


def mostrar_kpis(indicadores):
    cols = st.columns(len(indicadores))
    for col, (label, valor) in zip(cols, indicadores):
        with col:
            st.metric(label, numero(valor))


def mostrar_hallazgos(nombre_evento, inscripciones_evento, nombre_mes, inscripciones_mes, certificados_pagados):
    st.markdown(
        f"**Evento con más inscripciones:** {nombre_evento} ({numero(inscripciones_evento)})\n\n"
        f"**Mes de mayor actividad:** {nombre_mes} ({numero(inscripciones_mes)} inscripciones)\n\n"
        f"**Certificados pagados:** {numero(certificados_pagados)}"
    )


def mostrar_tarjetas_certificados(tarjetas):
    cols = st.columns(len(tarjetas))
    for col, (label, valor) in zip(cols, tarjetas):
        with col:
            st.metric(label, valor)


def mostrar_tabla_eventos(tabla):
    st.dataframe(tabla, use_container_width=True)


try:
    df_events, df_inscripciones = cargar_eventos(DB_NAME, MONGO_URI)
except Exception as e:
    st.error(f"Error al cargar datos desde MongoDB: {e}")
    st.stop()

etiquetas = T.etiquetas_eventos(df_events)

st.sidebar.header("Filtros")

fechas_validas = pd.to_datetime(df_events["date"], errors="coerce", utc=True).dt.date
fecha_min = fechas_validas.min() if not fechas_validas.isna().all() else None
fecha_max = fechas_validas.max() if not fechas_validas.isna().all() else None

rango = st.sidebar.date_input("Rango de fechas", value=(fecha_min, fecha_max),
                              min_value=fecha_min, max_value=fecha_max) if fecha_min and fecha_max else None

evento_sel = st.sidebar.selectbox("Evento", ["Todos"] + df_events["event_id"].astype(str).tolist())
modalidad = st.sidebar.selectbox("Modalidad", ["Todas"] + sorted(df_events["modality"].dropna().unique().tolist()) if "modality" in df_events.columns else ["Todas"])
empresa = st.sidebar.selectbox("Empresa", ["Todas"] + sorted(df_events["companyName"].dropna().unique().tolist()) if "companyName" in df_events.columns else ["Todas"])
categoria = st.sidebar.selectbox("Categoría", ["Todas"] + sorted(df_events["category"].dropna().unique().tolist()) if "category" in df_events.columns else ["Todas"])

eventos_filtrados = T.aplicar_filtros_eventos(df_events, rango=rango, evento=evento_sel,
                                              modalidad=modalidad, empresa=empresa, categoria=categoria)
datos = T.filtrar_inscripciones_por_eventos(df_inscripciones, eventos_filtrados)

st.title("Exploración por eventos")
st.caption("Laboral.AI | Desempeño de eventos, inscripciones, participantes y certificados")
st.divider()

kpis = M.calcular_kpis_eventos(eventos_filtrados, datos)
mostrar_kpis([
    ("Total de eventos registrados", kpis["total_eventos"]),
    ("Total de inscripciones", kpis["total_inscripciones"]),
    ("Total de participantes distintos", kpis["participantes_unicos"]),
    ("Total de asistencias registradas", kpis["asistencias"]),
    ("Total de eventos con inscripciones", kpis["eventos_con_inscripciones"]),
])

hall = M.hallazgos_clave(eventos_filtrados, datos, etiquetas)
mes_nombre, mes_cant = T.obtener_mes_mayor_actividad(datos)
mostrar_hallazgos(hall["nombre_mejor_evento"], hall["mayor_registro_evento"], mes_nombre, mes_cant, kpis["certificados_pagados"])

titulo_seccion("Desempeño de eventos")
col1, col2 = st.columns(2, gap="medium")
with col1:
    with st.container(border=True):
        st.subheader("Total de inscripciones por evento")
        grafico(G.inscripciones_por_evento(M.inscripciones_por_evento(datos), etiquetas), 370)
with col2:
    with st.container(border=True):
        st.subheader("Evolución del total de inscripciones")
        grafico(G.evolucion_inscripciones(M.evolucion_inscripciones_mensual(datos)), 370)

titulo_seccion("Estados y modalidad")
col3, col4 = st.columns(2, gap="medium")
with col3:
    with st.container(border=True):
        st.subheader("Estados de inscripción")
        grafico(G.estados_inscripcion(M.estados_inscripcion(datos)))
with col4:
    with st.container(border=True):
        st.subheader("Eventos por modalidad")
        grafico(G.eventos_por_modalidad(M.eventos_por_modalidad(eventos_filtrados)))

titulo_seccion("Categorías y tipos de eventos")
col5, col6 = st.columns(2, gap="medium")
with col5:
    with st.container(border=True):
        st.subheader("Inscripciones por categoría")
        grafico(G.inscripciones_por_categoria(M.inscripciones_por_categoria(datos)))
with col6:
    with st.container(border=True):
        st.subheader("Eventos por tipo")
        grafico(G.eventos_por_tipo(M.eventos_por_tipo(eventos_filtrados)))

titulo_seccion("Empresas organizadoras")
with st.container(border=True):
    st.subheader("Inscripciones por empresa")
    grafico(G.inscripciones_por_empresa(M.inscripciones_por_empresa(datos)))

titulo_seccion("Análisis de participantes")
col7, col8 = st.columns(2, gap="medium")
with col7:
    with st.container(border=True):
        st.subheader("Creación de cuentas respecto al evento")
        grafico(G.creacion_cuentas(M.participantes_creacion_cuenta(datos, eventos_filtrados)), 350)
with col8:
    with st.container(border=True):
        st.subheader("Relación de los participantes con Laboral.AI")
        grafico(G.relacion_laboralai(M.participantes_relacion_laboralai(datos)), 350)

titulo_seccion("Análisis de certificados")
cert = M.kpis_certificados(eventos_filtrados, datos)
mostrar_tarjetas_certificados([
    ("Eventos que ofrecen certificado", numero(cert["eventos_con_certificado"])),
    ("Certificados marcados como pagados", numero(cert["certificados_pagados"])),
    ("Importe asociado a certificados pagados", cert["importe_mostrado"]),
])
st.caption("Importe estimado a partir del precio y el estado de pago registrados para los certificados.")
if cert["sin_precio_valido"] > 0:
    st.warning(f"Hay {cert['sin_precio_valido']} certificados marcados como pagados sin importe calculable.")
with st.container(border=True):
    st.subheader("Certificados pagados por evento")
    grafico(G.certificados_por_evento(M.certificados_por_evento(datos), etiquetas))

titulo_seccion("Detalle de eventos")
with st.container(border=True):
    tabla = M.detalle_eventos(eventos_filtrados, datos)
    if not tabla.empty and "event_id" in tabla.columns:
        tabla["Evento"] = tabla["event_id"].map(lambda x: etiquetas.get(str(x), "Sin título"))
    mostrar_tabla_eventos(tabla)

st.caption("Fuente: MongoDB | Colecciones events, eventguests y users. Todos los indicadores responden a los filtros.")
