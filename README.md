# Dashboards Laboral.AI — Plantilla Modular para Equipo de Data

Plantilla multipágina en **Streamlit** diseñada para trabajar en equipo con **Git Flow** sin conflictos de merge, separando extracción/caché, transformaciones, métricas, gráficos e interfaz por cada dominio.

## Estructura del proyecto

```text
Dashboards_LaboralAI/
├── app.py                  # Router principal (st.navigation + st.Page)
├── config.py               # Configuración centralizada (.env, Mongo, caché)
├── mongodb.py              # Conexión segura a MongoDB y normalización de ObjectId
├── cache.py                # Caché en disco (pkl / parquet / csv) y metadatos
├── styles.py               # Estilos CSS globales
├── ui_helpers.py           # Componentes UI compartidos (control de caché, figuras vacías)
├── pages/                  # Un archivo independiente por página (evita conflictos Git Flow)
│   ├── 0_Inicio.py         # Portada con redirección (st.switch_page) y panel de caché
│   ├── 1_Postulantes.py    # UI del módulo Postulantes
│   ├── 2_Empresas.py       # UI del módulo Empresas
│   └── 3_Eventos.py        # UI del módulo Eventos
├── src/                    # Lógica de negocio modular por dominio
│   ├── postulantes/
│   │   ├── cargar_datos.py     # Extracción MongoDB + @st.cache_data + caché en disco
│   │   ├── transformaciones.py # Limpieza, normalización y filtros puros
│   │   ├── metricas.py         # KPIs y tablas resumen
│   │   └── graficos.py         # Figuras Plotly
│   ├── empresas/           # Misma estructura para Empresas
│   └── eventos/            # Misma estructura para Eventos
└── tests/                  # Pruebas unitarias con pytest
```

## Cómo funciona el caché de DataFrames (2 niveles)

1. **Nivel 1 — Caché en disco (`cache/<modulo>.pkl`)**:
   - Evita consultar MongoDB en cada reinicio del servidor o recarga completa.
   - Se actualiza manualmente desde `Inicio & Caché` o desde el sidebar de cada página.
   - Soporta formatos `.pkl` (por defecto, ideal para datos semiestructurados de MongoDB con listas/dicts), `.parquet` y `.csv`.
2. **Nivel 2 — Caché en memoria (`@st.cache_data`)**:
   - Cada `cargar_<modulo>()` lee el archivo en disco una sola vez y lo mantiene en memoria durante `CACHE_TTL_SECONDS` (por defecto 3600s).
   - Al ejecutar `actualizar_cache_<modulo>()`, se reescribe el archivo en disco y se invoca `.clear()` sobre la función cacheada para reflejar los nuevos datos al instante.

## Flujo de trabajo recomendado (Git Flow)

- **Equipo Postulantes**: trabaja únicamente en `src/postulantes/` y `pages/1_Postulantes.py`.
- **Equipo Empresas**: trabaja únicamente en `src/empresas/` y `pages/2_Empresas.py`.
- **Equipo Eventos**: trabaja únicamente en `src/eventos/` y `pages/3_Eventos.py`.
- `app.py` solo registra las rutas `st.Page(...)`, por lo que rara vez cambia entre ramas.
- La carpeta `cache/` está ignorada en `.gitignore` para no generar conflictos binarios en git.

## Ejecución local

1. Crea tu entorno e instala dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configura variables de entorno:
   ```bash
   cp .env.example .env
   ```
3. Inicia la aplicación:
   ```bash
   streamlit run app.py
   ```
   > Si aún no tienes conexión a MongoDB en local, puedes usar los botones **🧪 Demo** en la interfaz para poblar datos de ejemplo y desarrollar métricas/gráficos inmediatamente.
4. Ejecuta las pruebas:
   ```bash
   pytest
   ```
