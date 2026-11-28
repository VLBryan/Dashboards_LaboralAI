# Laboral.AI Dashboard (Unificado)

Dashboard multipágina en Streamlit con módulos de **Postulantes** y **Eventos**.

## Estructura

```
app.py                  # Home / router
config.py               # Configuración Mongo/TTL
pages/
  1_Postulantes.py
  3_Eventos.py
src/
  cargar_datos.py       # Postulantes
  metricas.py
  graficos.py
  eventos/
    cargar_datos.py     # Eventos (Mongo: events, eventguests, users)
    transformaciones.py # Filtros
    metricas.py         # KPIs
    graficos.py         # Plotly
```

## Configuración

1. Crear `.env` en la raíz (ver `.env.example`).
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `streamlit run app.py`

## Notas
- No se usan archivos físicos para caché: los DataFrames se mantienen en RAM con `@st.cache_data`.
- Los datos se leen desde MongoDB (colecciones `events`, `eventguests`, `users`).
