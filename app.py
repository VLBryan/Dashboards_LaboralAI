# app.py
import streamlit as st

st.set_page_config(
    page_title="Laboral.AI Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Laboral.AI Dashboard")
st.caption("Selecciona una sección en el menú lateral.")

st.markdown("""
### Secciones disponibles
- **Postulantes / Candidatos** → análisis de candidatos activos.
- **Eventos** → desempeño de eventos, inscripciones, participantes y certificados.

Usa el menú de la izquierda para navegar.
""")
