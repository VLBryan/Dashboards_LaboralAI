from src.eventos.cargar_datos import (
    cargar_eventos,
    actualizar_cache_eventos
)

from src.eventos.metricas import *
from src.eventos.graficos import *


import streamlit as st

from styles import cargar_estilos


cargar_estilos()

df = cargar_eventos()

st.title("📊 Dashboard Eventos")