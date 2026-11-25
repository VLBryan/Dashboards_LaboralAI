"""Página principal: centro de redirección a dashboards y administración de caché."""

from __future__ import annotations

import streamlit as st

from mongodb import MongoConnectionError
from src.empresas import (
    actualizar_cache_empresas,
    obtener_estado_cache_empresas,
)
from src.eventos import (
    actualizar_cache_eventos,
    obtener_estado_cache_eventos,
)
from src.postulantes import (
    actualizar_cache_postulantes,
    obtener_estado_cache_postulantes,
)

st.title("📊 Dashboards Laboral.AI")
st.caption(
    "Plantilla modular para el equipo de Data. Selecciona un módulo para abrir su "
    "dashboard o actualiza el caché local de DataFrames."
)

MODULOS = [
    {
        "key": "postulantes",
        "titulo": "🧑‍💼 Postulantes",
        "descripcion": "Perfiles activos, disponibilidad, modalidad y profesiones en CV.",
        "page_path": "pages/1_Postulantes.py",
        "estado_fn": obtener_estado_cache_postulantes,
        "actualizar_fn": actualizar_cache_postulantes,
    },
    {
        "key": "empresas",
        "titulo": "🏢 Empresas",
        "descripcion": "Empresas registradas, sectores, tamaños y ofertas activas.",
        "page_path": "pages/2_Empresas.py",
        "estado_fn": obtener_estado_cache_empresas,
        "actualizar_fn": actualizar_cache_empresas,
    },
    {
        "key": "eventos",
        "titulo": "🎟️ Eventos",
        "descripcion": "Eventos realizados, inscritos, asistentes y tasas de asistencia.",
        "page_path": "pages/3_Eventos.py",
        "estado_fn": obtener_estado_cache_eventos,
        "actualizar_fn": actualizar_cache_eventos,
    },
]

# Botón global para generar datos demo en los 3 módulos con un clic
col_top_1, col_top_2 = st.columns([3, 1])
with col_top_2:
    if st.button("🧪 Cargar demo en todos", width="stretch"):
        for mod in MODULOS:
            mod["actualizar_fn"](usar_demo=True)
        st.success("Caché demo generado para Postulantes, Empresas y Eventos.")
        st.rerun()

st.divider()

cols = st.columns(len(MODULOS))
for col, mod in zip(cols, MODULOS):
    with col:
        with st.container(border=True):
            st.subheader(mod["titulo"])
            st.write(mod["descripcion"])

            meta = mod["estado_fn"]()
            if meta["existe"] and meta["actualizado_en"] is not None:
                fecha_txt = meta["actualizado_en"].strftime("%Y-%m-%d %H:%M")
                st.success(f"Caché listo ({meta['tamano_kb']} KB) · {fecha_txt}")
            else:
                st.info("Sin caché en disco todavía.")

            if st.button(
                f"Ir a {mod['titulo'].split(' ', 1)[1]} →",
                key=f"nav_{mod['key']}",
                type="primary",
                width="stretch",
            ):
                st.switch_page(mod["page_path"])

            btn_mongo, btn_demo = st.columns(2)
            with btn_mongo:
                if st.button("🔄 MongoDB", key=f"mongo_{mod['key']}", width="stretch"):
                    try:
                        with st.spinner(f"Actualizando {mod['key']}..."):
                            mod["actualizar_fn"](usar_demo=False)
                        st.toast(f"Caché de {mod['key']} actualizado.", icon="✅")
                        st.rerun()
                    except MongoConnectionError as exc:
                        st.error(f"Error MongoDB: {exc}")
            with btn_demo:
                if st.button("🧪 Demo", key=f"demo_{mod['key']}", width="stretch"):
                    mod["actualizar_fn"](usar_demo=True)
                    st.toast(f"Demo cargada para {mod['key']}.", icon="✅")
                    st.rerun()
