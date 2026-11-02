import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html

# Inicializar app con tema Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Exposición del servidor Flask (indispensable para despliegues como Render)
server = app.server

# Cargar CSVs livianos
df_depto = pd.read_csv("data/muertes_departamento.csv")
df_mes = pd.read_csv("data/muertes_mes.csv")
df_top_violentas = pd.read_csv("data/top5_violentas.csv")
df_menor_mortalidad = pd.read_csv("data/top10_menor_mortalidad.csv")
df_top_causas = pd.read_csv("data/top10_causas.csv")
df_sexo_depto = pd.read_csv("data/muertes_sexo_depto.csv")
df_edad = pd.read_csv("data/muertes_edad.csv")

# Figuras Plotly Express
fig_lineas = px.line(
    df_mes,
    x="NOMBRE_MES",
    y="TOTAL_MUERTES",
    title="Evolución Mensual de la Mortalidad",
    markers=True,
)

fig_barras_violencia = px.bar(
    df_top_violentas,
    x="MUNICIPIO",
    y="TOTAL_HOMICIDIOS",
    color="DEPARTAMENTO",
    title="Top 5 Ciudades más Violentas (Homicidios)",
)

fig_pie_menor = px.pie(
    df_menor_mortalidad,
    values="TOTAL_MUERTES",
    names="MUNICIPIO",
    title="Top 10 Ciudades con Menor Mortalidad",
)

fig_barras_sexo = px.bar(
    df_sexo_depto,
    x="DEPARTAMENTO",
    y="TOTAL_MUERTES",
    color="SEXO_NOMBRE",
    barmode="stack",
    title="Mortalidad por Sexo y Departamento",
)

fig_histograma_edad = px.bar(
    df_edad,
    x="RANGO_EDAD",
    y="TOTAL_MUERTES",
    title="Distribución de Mortalidad por Rangos de Edad",
)

# Maquetado de la Interfaz
app.layout = dbc.Container(
    [
        html.H1(
            "Análisis de Mortalidad en Colombia (2019)",
            className="text-center my-4 text-primary",
        ),
        # Fila 1: Línea temporal y Barras violencia
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig_lineas), width=6),
                dbc.Col(dcc.Graph(figure=fig_barras_violencia), width=6),
            ],
            className="mb-4",
        ),
        # Fila 2: Torta menor mortalidad y Barras apiladas sexo
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig_pie_menor), width=6),
                dbc.Col(dcc.Graph(figure=fig_barras_sexo), width=6),
            ],
            className="mb-4",
        ),
        # Fila 3: Tabla de causas y Barras de edad
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5(
                            "Top 10 Principales Causas de Muerte (CIE-10)",
                            className="text-center mb-3",
                        ),
                        dash_table.DataTable(
                            data=df_top_causas.to_dict("records"),
                            columns=[
                                {"name": i, "id": i} for i in df_top_causas.columns
                            ],
                            style_table={"overflowX": "auto"},
                            style_cell={"textAlign": "left", "padding": "8px"},
                            style_header={
                                "backgroundColor": "rgb(230, 230, 230)",
                                "fontWeight": "bold",
                            },
                            page_size=10,
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(dcc.Graph(figure=fig_histograma_edad), width=6),
            ],
            className="mb-4",
        ),
    ],
    fluid=True,
)

if __name__ == "__main__":
    app.run(debug=True)