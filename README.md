# Dashboards Laboral.AI — Plantilla Modular para Equipo de Data

Plantilla multipágina en **Streamlit** diseñada para trabajar en equipo con **Git Flow** sin conflictos de merge, con caché de DataFrames **exclusivamente en memoria** (`@st.cache_data`) para proteger datos sensibles.

## Estructura del proyecto

```text
Dashboards_LaboralAI/
├── app.py                  # Router principal (st.navigation + st.Page)
├── config.py               # Configuración centralizada (.env, MongoDB, TTL de caché)
├── mongodb.py              # Conexión segura a MongoDB y normalización de ObjectId
├── cache.py                # Helpers de caché en memoria (invalidación y registro en sesión)
├── styles.py               # Estilos CSS globales
├── ui_helpers.py           # Sidebar de caché en memoria y carga segura desde MongoDB
├── pages/                  # Un archivo independiente por página (evita conflictos Git Flow)
│   ├── 0_Inicio.py         # Portada con redirección (st.switch_page) y limpieza de caché
│   ├── 1_Postulantes.py    # Página base en blanco para Postulantes
│   ├── 2_Empresas.py       # Página base en blanco para Empresas
│   └── 3_Eventos.py        # Página base en blanco para Eventos
├── src/                    # Lógica de negocio modular por dominio
│   ├── postulantes/
│   │   ├── cargar_datos.py     # Extracción MongoDB + @st.cache_data en memoria
│   │   ├── transformaciones.py # Limpieza, normalización y filtros puros
│   │   ├── metricas.py         # KPIs y tablas resumen
│   │   └── graficos.py         # Figuras Plotly
│   ├── empresas/           # Misma estructura para Empresas
│   └── eventos/            # Misma estructura para Eventos
└── tests/                  # Pruebas unitarias con pytest
```

## Manejo de caché de DataFrames (solo en memoria)

- **Sin archivos físicos**: no se generan `.csv`, `.pkl` ni `.parquet` en disco, evitando exponer datos sensibles en local o en el repositorio.
- **Caché en RAM con `@st.cache_data`**: cada función `cargar_<modulo>()` consulta MongoDB una sola vez y mantiene el DataFrame en memoria durante `CACHE_TTL_SECONDS` (por defecto `3600` segundos).
- **Invalidación manual**: desde `Inicio & Caché` o desde el sidebar de cada página puedes limpiar el caché en memoria (`actualizar_cache_<modulo>()`) para forzar una nueva lectura desde MongoDB.

## Flujo de trabajo en equipo (Git Flow)

- **Sub-equipo Postulantes**: trabaja en `src/postulantes/` y `pages/1_Postulantes.py`.
- **Sub-equipo Empresas**: trabaja en `src/empresas/` y `pages/2_Empresas.py`.
- **Sub-equipo Eventos**: trabaja en `src/eventos/` y `pages/3_Eventos.py`.
- `app.py` solo registra el mapa de navegación `st.Page(...)`, evitando conflictos entre ramas.

## Ejecución local

1. Activa el entorno virtual e instala dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configura tus credenciales locales:
   ```bash
   cp .env.example .env
   ```
3. Inicia la aplicación:
   ```bash
   streamlit run app.py
   ```
4. Ejecuta las pruebas:
   ```bash
   pytest
   ```
