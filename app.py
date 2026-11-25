import streamlit as st

from src.postulantes import actualizar_cache_postulantes
from src.empresas import actualizar_cache_empresas
from src.eventos import actualizar_cache_eventos

st.set_page_config(
    page_title="Laboral.AI Admin",
    layout="wide"
)

st.title("⚙️ Administración de Datos")


col1, col2, col3 = st.columns(3)

with col1:

    if st.button("🔄 Actualizar Postulantes"):
        actualizar_cache_postulantes()

with col2:

    if st.button("🔄 Actualizar Empresas"):
        actualizar_cache_empresas()

with col3:

    if st.button("🔄 Actualizar Eventos"):
        actualizar_cache_eventos()