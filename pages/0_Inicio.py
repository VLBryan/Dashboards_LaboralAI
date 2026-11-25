"""Página principal: centro de redirección a dashboards y limpieza de caché en memoria."""

from __future__ import annotations

import streamlit as st

from cache import obtener_actualizacion_memoria
from src.empresas import actualizar_cache_empresas
from src.eventos import actualizar_cache_eventos
from src.postulantes import actualizar_cache_postulantes

st.title("📊 Dashboards Laboral.AI")
st.caption(
    "Plantilla modular para el equipo de Data. Selecciona un módulo para abrir su "
    "página o limpia el caché en memoria para forzar una nueva lectura desde MongoDB."
)

MODULOS = [
    {
        "key": "postulantes",
        "titulo": "🧑‍💼 Postulantes",
        "descripcion": "Módulo en `src/postulantes/` y vista en `pages/1_Postulantes.py`.",
        "page_path": "pages/1_Postulantes.py",
        "actualizar_fn": actualizar_cache_postulantes,
    },
    {
        "key": "empresas",
        "titulo": "🏢 Empresas",
        "descripcion": "Módulo en `src/empresas/` y vista en `pages/2_Empresas.py`.",
        "page_path": "pages/2_Empresas.py",
        "actualizar_fn": actualizar_cache_empresas,
    },
    {
        "key": "eventos",
        "titulo": "🎟️ Eventos",
        "descripcion": "Módulo en `src/eventos/` y vista en `pages/3_Eventos.py`.",
        "page_path": "pages/3_Eventos.py",
        "actualizar_fn": actualizar_cache_eventos,
    },
]

col_izq, col_der = st.columns([3, 1])
with col_der:
    if st.button("🧹 Limpiar todo el caché", width="stretch"):
        for mod in MODULOS:
            mod["actualizar_fn"]()
        st.toast("Caché en memoria limpiado en todos los módulos.", icon="✅")
        st.rerun()

st.divider()

cols = st.columns(len(MODULOS))
for col, mod in zip(cols, MODULOS):
    with col:
        with st.container(border=True):
            st.subheader(mod["titulo"])
            st.write(mod["descripcion"])

            ultima = obtener_actualizacion_memoria(mod["key"])
            if ultima is not None:
                st.caption(f"⚡ En memoria desde: {ultima.strftime('%H:%M:%S')}")
            else:
                st.caption("⚡ Aún no cargado en memoria en esta sesión.")

            if st.button(
                f"Ir a {mod['titulo'].split(' ', 1)[1]} →",
                key=f"nav_{mod['key']}",
                type="primary",
                width="stretch",
            ):
                st.switch_page(mod["page_path"])

            if st.button(
                "🔄 Limpiar caché en memoria",
                key=f"clear_{mod['key']}",
                width="stretch",
            ):
                mod["actualizar_fn"]()
                st.toast(f"Caché de {mod['key']} limpiado.", icon="🔄")
                st.rerun()
