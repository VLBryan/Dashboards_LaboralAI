"""Configuración centralizada del proyecto.

Lee las variables de entorno desde `.env` (si existe) y expone los parámetros
de conexión a MongoDB y de caché en memoria (`@st.cache_data`).
No se define ruta de caché en disco para evitar almacenar datos sensibles localmente.
"""

import os

from dotenv import load_dotenv

# Carga variables definidas en el archivo .env en la raíz del proyecto
load_dotenv()

# -------------------------
# Configuración de MongoDB
# -------------------------
MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# Se aceptan LABORAL_DB o DB_NAME por compatibilidad con el entorno del equipo
DB_NAME: str = os.getenv("LABORAL_DB") or os.getenv("DB_NAME", "laboral-ai-dev")
MONGO_TIMEOUT_MS: int = int(os.getenv("MONGO_TIMEOUT_MS", "5000"))

# -------------------------
# Configuración de Caché en Memoria
# -------------------------
# Tiempo de vida (en segundos) para @st.cache_data en RAM (por defecto 1 hora = 3600s)
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
