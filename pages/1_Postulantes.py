from src.postulantes.cargar_datos import (
    cargar_postulantes,
    actualizar_cache_postulantes
)

from src.postulantes.metricas import *
from src.postulantes.graficos import *


import streamlit as st

from styles import cargar_estilos


cargar_estilos()

df = cargar_postulantes()

st.title("📊 Dashboard Postulantes")