"""Estilos CSS globales compartidos por todas las páginas del dashboard."""

import streamlit as st


def cargar_estilos() -> None:
    """Inyecta estilos CSS consistentes en la aplicación Streamlit."""
    st.markdown(
        """
        <style>
        .main {
            padding-top: 1rem;
        }
        h1 {
            font-weight: 700;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.9rem;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
