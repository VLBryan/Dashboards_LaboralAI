"""Punto de entrada principal (`streamlit run app.py`).

Arquitectura pensada para Git Flow en equipo:
- `app.py` únicamente configura la app, carga estilos globales y redirige a las
  páginas independientes mediante `st.navigation` + `st.Page`.
- Cada miembro/sub-equipo trabaja exclusivamente en su archivo dentro de `pages/`
  y en su carpeta correspondiente dentro de `src/` (`postulantes`, `empresas`, `eventos`),
  evitando conflictos de merge en Git Flow.
"""

import streamlit as st

from styles import cargar_estilos

st.set_page_config(
    page_title="Laboral.AI | Dashboards",
    page_icon="📊",
    layout="wide",
)

cargar_estilos()

# Registro central de páginas independientes (cada archivo vive aislado en `pages/`).
# Si agregas un nuevo dominio, solo crea `src/<nuevo>/`, `pages/4_<Nuevo>.py`
# y añade aquí una entrada `st.Page(...)`.
paginas = [
    st.Page("pages/0_Inicio.py", title="Inicio & Caché", icon="🏠", default=True),
    st.Page("pages/1_Postulantes.py", title="Postulantes", icon="🧑‍💼"),
    st.Page("pages/2_Empresas.py", title="Empresas", icon="🏢"),
    st.Page("pages/3_Eventos.py", title="Eventos", icon="🎟️"),
]

navegacion = st.navigation(paginas)
navegacion.run()
