import plotly.express as px


COLOR_INSCRIPCIONES = "#173F6D"
COLOR_EVOLUCION = "#8CC04B"
COLOR_ESTADOS = "#624C8E"
COLOR_MODALIDAD = "#6DB3BB"
COLOR_CATEGORIAS = "#F1921A"
COLOR_TIPOS = "#173F6D"
COLOR_EMPRESAS = "#6DB3BB"
COLOR_CREACION_CUENTAS = "#F8C64B"
COLOR_RELACION_USUARIOS = "#CF4786"
COLOR_CERTIFICADOS = "#12365B"


def tonos_grafico(color, cantidad):
    if cantidad <= 0:
        return []
    color = color.lstrip("#")
    rojo = int(color[0:2], 16)
    verde = int(color[2:4], 16)
    azul = int(color[4:6], 16)
    resultado = []
    for indice in range(cantidad):
        factor = 0.0 if cantidad == 1 else 0.60 * indice / (cantidad - 1)
        r = round(rojo + (255 - rojo) * factor)
        g = round(verde + (255 - verde) * factor)
        b = round(azul + (255 - azul) * factor)
        resultado.append(f"rgb({r},{g},{b})")
    return resultado


def color_transparente(color, opacidad=0.18):
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return f"rgba({r},{g},{b},{opacidad})"


def inscripciones_por_evento(fig_df, etiquetas, color=COLOR_INSCRIPCIONES):
    if fig_df.empty:
        return None
    ranking = fig_df.sort_values("Inscripciones", ascending=False).copy()
    ranking["_evento_id"] = ranking["event_id"].astype(str)
    ranking["Evento"] = ranking["event_id"].map(lambda x: etiquetas.get(str(x), "Sin título"))
    fig = px.bar(ranking, x="Inscripciones", y="_evento_id", orientation="h", text="Inscripciones",
                 custom_data=["Evento"], color_discrete_sequence=[color])
    fig.update_traces(marker_color=tonos_grafico(color, len(ranking)),
                      hovertemplate="%{customdata[0]}<br>Inscripciones: %{x}<extra></extra>")
    fig.update_yaxes(title=None, tickmode="array", tickvals=ranking["_evento_id"].tolist(),
                     ticktext=ranking["Evento"].tolist(), categoryorder="total ascending")
    fig.update_layout(height=370)
    return fig


def evolucion_inscripciones(fig_df, color=COLOR_EVOLUCION):
    if fig_df.empty:
        return None
    fig = px.line(fig_df, x="Mes", y="Inscripciones", markers=True)
    fig.update_traces(line=dict(color=color, width=3), marker=dict(color=color, size=7),
                      fill="tozeroy", fillcolor=color_transparente(color, 0.18))
    fig.update_layout(showlegend=False, height=370)
    return fig


def estados_inscripcion(fig_df, color=COLOR_ESTADOS):
    if fig_df.empty:
        return None
    fig = px.bar(fig_df, x="Estado", y="Cantidad", text="Cantidad", color_discrete_sequence=[color])
    fig.update_traces(marker_color=tonos_grafico(color, len(fig_df)))
    fig.update_layout(showlegend=False)
    return fig


def eventos_por_modalidad(fig_df, color=COLOR_MODALIDAD):
    if fig_df.empty:
        return None
    colores = tonos_grafico(color, len(fig_df))
    fig = px.pie(fig_df, names="Modalidad", values="Eventos", hole=0.58, color_discrete_sequence=colores)
    fig.update_traces(marker=dict(colors=colores))
    return fig


def inscripciones_por_categoria(fig_df, color=COLOR_CATEGORIAS):
    if fig_df.empty:
        return None
    fig = px.bar(fig_df, x="Inscripciones", y="category", orientation="h", color_discrete_sequence=[color])
    fig.update_traces(marker_color=tonos_grafico(color, len(fig_df)))
    fig.update_yaxes(title=None, categoryorder="total ascending")
    return fig


def eventos_por_tipo(fig_df, color=COLOR_TIPOS):
    if fig_df.empty:
        return None
    fig = px.bar(fig_df, x="Tipo", y="Eventos", color_discrete_sequence=[color])
    fig.update_traces(marker_color=tonos_grafico(color, len(fig_df)))
    return fig


def inscripciones_por_empresa(fig_df, color=COLOR_EMPRESAS):
    if fig_df.empty:
        return None
    fig = px.bar(fig_df, x="Inscripciones", y="Empresa", orientation="h", color_discrete_sequence=[color])
    fig.update_traces(marker_color=tonos_grafico(color, len(fig_df)))
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def creacion_cuentas(fig_df, color=COLOR_CREACION_CUENTAS):
    if fig_df.empty:
        return None
    orden_momentos = ["Antes del evento", "El mismo día del evento", "Después del evento",
                      "Sin cuenta identificada", "Sin fecha suficiente"]
    conteo = fig_df["momento_cuenta"].value_counts().reindex(orden_momentos, fill_value=0)
    categorias_visibles = ["Antes del evento", "El mismo día del evento", "Después del evento"] + \
        [c for c in orden_momentos[3:] if conteo[c] > 0]
    tabla = conteo.reindex(categorias_visibles).rename_axis("Momento").reset_index(name="Participantes")
    colores = tonos_grafico(color, len(tabla))
    fig = px.bar(tabla, x="Participantes", y="Momento", orientation="h", text="Participantes",
                 color_discrete_sequence=[color])
    fig.update_traces(marker_color=colores, textposition="outside", cliponaxis=False,
                      hovertemplate="%{y}<br>Participantes: %{x}<extra></extra>")
    fig.update_yaxes(title=None, categoryorder="array", categoryarray=list(reversed(categorias_visibles)))
    fig.update_xaxes(title="Participantes distintos", rangemode="tozero")
    fig.update_layout(showlegend=False, height=350, paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                      margin=dict(l=15, r=35, t=20, b=35))
    return fig


def relacion_laboralai(fig_series, color=COLOR_RELACION_USUARIOS):
    if fig_series is None or (hasattr(fig_series, "empty") and fig_series.empty):
        return None
    tabla = fig_series.rename_axis("Tipo").reset_index(name="Participantes")
    colores = tonos_grafico(color, len(tabla))
    fig = px.pie(tabla, names="Tipo", values="Participantes", hole=0.58, color_discrete_sequence=colores)
    fig.update_traces(marker=dict(colors=colores))
    fig.update_layout(height=350)
    return fig


def certificados_por_evento(fig_df, etiquetas, color=COLOR_CERTIFICADOS):
    if fig_df.empty:
        return None
    df = fig_df.sort_values("Certificados pagados", ascending=False).copy()
    df["_evento_id"] = df["event_id"].astype(str)
    df["Evento"] = df["event_id"].map(lambda x: etiquetas.get(str(x), "Sin título"))
    fig = px.bar(df, x="Certificados pagados", y="_evento_id", orientation="h", text="Certificados pagados",
                 custom_data=["Evento"], color_discrete_sequence=[color])
    fig.update_traces(marker_color=tonos_grafico(color, len(df)),
                      hovertemplate="%{customdata[0]}<br>Certificados pagados: %{x}<extra></extra>")
    fig.update_yaxes(title=None, tickmode="array", tickvals=df["_evento_id"].tolist(),
                     ticktext=df["Evento"].tolist(), categoryorder="total ascending")
    return fig
