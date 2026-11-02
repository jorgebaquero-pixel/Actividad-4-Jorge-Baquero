Python
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html

# 1. Inicializar la aplicación web con tema Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Exposición obligatoria del servidor Flask para despliegue en Render
server = app.server

# 2. Cargar los datos preprocesados desde la carpeta data/
df_depto = pd.read_csv("data/muertes_departamento.csv")
df_mes = pd.read_csv("data/muertes_mes.csv")
df_top_violentas = pd.read_csv("data/top5_violentas.csv")
df_menor_mortalidad = pd.read_csv("data/top10_menor_mortalidad.csv")
df_top_causas = pd.read_csv("data/top10_causas.csv")
df_sexo_depto = pd.read_csv("data/muertes_sexo_depto.csv")
df_edad = pd.read_csv("data/muertes_edad.csv")

# 3. GeoJSON público de departamentos de Colombia
geojson_colombia = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239f37974da7e64bb49f442e10f4432f74/colombia.geo.json"

# ---------------------------------------------------------
# 4. CONSTRUCCIÓN DE LAS 7 VISUALIZACIONES INTERACTIVAS
# ---------------------------------------------------------

# 1. Mapa coroplético por departamento
fig_mapa = px.choropleth(
    df_depto,
    geojson=geojson_colombia,
    locations="DEPARTAMENTO",
    featureidkey="properties.NOMBRE_DPT",
    color="TOTAL_MUERTES",
    color_continuous_scale="Reds",
    title="1. Distribución Total de Muertes por Departamento (2019)",
    labels={"TOTAL_MUERTES": "Total Defunciones", "DEPARTAMENTO": "Departamento"},
)
fig_mapa.update_geos(fitbounds="locations", visible=False)

# 2. Gráfico de líneas (Evolución Mensual)
fig_lineas = px.line(
    df_mes,
    x="NOMBRE_MES",
    y="TOTAL_MUERTES",
    title="2. Evolución Mensual de la Mortalidad",
    markers=True,
)

# 3. Gráfico de barras (Top 5 Homicidios)
fig_barras_violencia = px.bar(
    df_top_violentas,
    x="MUNICIPIO",
    y="TOTAL_HOMICIDIOS",
    color="DEPARTAMENTO",
    title="3. Top 5 Ciudades más Violentas (Homicidios X95)",
)

# 4. Gráfico circular (Top 10 Menor Mortalidad)
fig_pie_menor = px.pie(
    df_menor_mortalidad,
    values="TOTAL_MUERTES",
    names="MUNICIPIO",
    title="4. Top 10 Ciudades con Menor Mortalidad",
)

# 5. Barras apiladas (Mortalidad por Sexo y Departamento)
fig_barras_sexo = px.bar(
    df_sexo_depto,
    x="DEPARTAMENTO",
    y="TOTAL_MUERTES",
    color="SEXO_NOMBRE",
    barmode="stack",
    title="5. Mortalidad por Sexo y Departamento",
)

# 6. Distribución por rangos de edad
fig_histograma_edad = px.bar(
    df_edad,
    x="RANGO_EDAD",
    y="TOTAL_MUERTES",
    title="6. Distribución por Rangos de Edad (GRUPO_EDAD1)",
    labels={"RANGO_EDAD": "Grupo de Edad", "TOTAL_MUERTES": "Total Defunciones"},
)

# ---------------------------------------------------------
# 5. MAQUETADO DE LA INTERFAZ WEB (LAYOUT)
# ---------------------------------------------------------
app.layout = dbc.Container(
    [
        html.H1(
            "Análisis de Mortalidad en Colombia (2019)",
            className="text-center my-4 text-primary fw-bold",
        ),
        # Fila 1: Mapa Coroplético y Evolución Mensual
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig_mapa), width=6),
                dbc.Col(dcc.Graph(figure=fig_lineas), width=6),
            ],
            className="mb-4",
        ),
        # Fila 2: Violencia y Menor Mortalidad
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig_barras_violencia), width=6),
                dbc.Col(dcc.Graph(figure=fig_pie_menor), width=6),
            ],
            className="mb-4",
        ),
        # Fila 3: Tabla Top 10 Causas y Comparación por Sexo
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5(
                            "7. Top 10 Principales Causas de Muerte (CIE-10)",
                            className="text-center mb-3 text-secondary",
                        ),
                        dash_table.DataTable(
                            id="tabla-top-causas",
                            data=df_top_causas.to_dict("records"),
                            columns=[{"name": col, "id": col} for col in df_top_causas.columns],
                            page_size=10,
                            style_table={"overflowX": "auto"},
                            style_header={
                                "backgroundColor": "#0d6efd",
                                "color": "white",
                                "fontWeight": "bold",
                                "textAlign": "center",
                            },
                            style_cell={
                                "textAlign": "left",
                                "padding": "10px",
                                "fontSize": "14px",
                                "whiteSpace": "normal",
                                "height": "auto",
                            },
                            style_cell_conditional=[
                                {
                                    "if": {"column_id": "Código CIE-10"},
                                    "width": "15%",
                                    "textAlign": "center",
                                }, 
                                {
                                    "if": {"column_id": "Total de Defunciones"},
                                    "width": "20%",
                                    "textAlign": "right",
                                },
                            ],
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(dcc.Graph(figure=fig_barras_sexo), width=6),
            ],
            className="mb-4",
        ),
        # Fila 4: Histograma por Rangos de Edad
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig_histograma_edad), width=12),
            ],
            className="mb-4",
        ),
    ],
    fluid=True,
)

if __name__ == "__main__":
    app.run(debug=True)