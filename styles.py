import streamlit as st

def cargar_estilos():

    st.markdown("""
    <style>

    .main {
        padding-top:1rem;
    }

    h1{
        font-weight:700;
    }

    [data-testid="stMetricValue"]{
        font-size:2rem;
    }

    </style>
    """,
    unsafe_allow_html=True)