from src.empresas.cargar_datos import (
    cargar_empresas,
    actualizar_cache_empresas
)

from src.empresas.metricas import *
from src.empresas.graficos import *

import streamlit as st

from styles import cargar_estilos


cargar_estilos()

df = cargar_empresas()

st.title("📊 Dashboard Empresas")