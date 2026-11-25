"""Configuración centralizada del proyecto.

Lee las variables de entorno desde `.env` (si existe) y expone valores por defecto
seguros para la conexión a MongoDB y la gestión de caché de DataFrames.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga variables definidas en el archivo .env en la raíz del proyecto
load_dotenv()

# -------------------------
# Configuración de MongoDB
# -------------------------
MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# Se aceptan LABORAL_DB (definido en .env.example) o DB_NAME para compatibilidad
DB_NAME: str = os.getenv("LABORAL_DB") or os.getenv("DB_NAME", "laboral-ai-dev")
MONGO_TIMEOUT_MS: int = int(os.getenv("MONGO_TIMEOUT_MS", "5000"))

# -------------------------
# Configuración de Caché
# -------------------------
CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", "./cache"))
# TTL en segundos para @st.cache_data (por defecto 1 hora = 3600s)
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
# Formato de persistencia en disco: "pkl" (recomendado para datos anidados de Mongo),
# "parquet" (muy rápido para tablas planas) o "csv".
CACHE_FORMAT: str = os.getenv("CACHE_FORMAT", "pkl").lower().lstrip(".")


def get_cache_path(module_name: str, fmt: str | None = None) -> Path:
    """Construye la ruta estándar de caché para un módulo de dominio.

    Ejemplo: `get_cache_path("postulantes")` -> `Path("./cache/postulantes.pkl")`
    """
    ext = (fmt or CACHE_FORMAT).lower().lstrip(".")
    return CACHE_DIR / f"{module_name}.{ext}"
