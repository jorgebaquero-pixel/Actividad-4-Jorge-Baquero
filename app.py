from dash import Dash, html, dcc, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Cargar Datos
df_depto = pd.read_csv("data/muertes_departamento.csv")
df_mes = pd.read_csv("data/muertes_mes.csv")
df_top_violentas = pd.read_csv("data/top5_violentas.csv")
df_menor_mortalidad = pd.read_csv("data/top10_menor_mortalidad.csv")
df_top_causas = pd.read_csv("data/top10_causas.csv")
df_sexo_depto = pd.read_csv("data/muertes_sexo_depto.csv")
df_edad = pd.read_csv("data/muertes_edad.csv")

# 1. MAPA
fig_mapa = px.scatter_map(
    df_depto, lat="Latitud", lon="Longitud", size="TOTAL_MUERTES", color="TOTAL_MUERTES",
    hover_name="DEPARTAMENTO", hover_data={"TOTAL_MUERTES": True, "Latitud": False, "Longitud": False},
    color_continuous_scale="Reds", size_max=40, zoom=4.5, center={"lat": 4.5709, "lon": -74.2973},
    map_style="open-street-map", title="1. Distribución de Muertes por Departamento"
)
fig_mapa.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

# 2. LÍNEAS
fig_lineas = px.line(df_mes, x="NOMBRE_MES", y="TOTAL_MUERTES", title="2. Evolución Mensual", markers=True)

# 3. BARRAS (HOMICIDIOS)
fig_barras_violencia = px.bar(
    df_top_violentas, x="MUNICIPIO", y="TOTAL_HOMICIDIOS", color="MUNICIPIO",
    title="3. Top 5 Ciudades más Violentas", labels={"MUNICIPIO": "Ciudad"}
)

# 4. CIRCULAR
fig_pie_menor = px.pie(df_menor_mortalidad, values="TOTAL_MUERTES", names="MUNICIPIO", title="4. Top 10 Menor Mortalidad")

# 5. BARRAS APILADAS
fig_barras_sexo = px.bar(df_sexo_depto, x="DEPARTAMENTO", y="TOTAL_MUERTES", color="SEXO_NOMBRE", barmode="stack", title="5. Mortalidad por Sexo")

# 6. HISTOGRAMA EDAD
fig_histograma_edad = px.bar(df_edad, x="RANGO_EDAD", y="TOTAL_MUERTES", color="RANGO_EDAD", title="6. Mortalidad por Rangos de Edad")

# DISEÑO DE LA INTERFAZ
app.layout = dbc.Container([
    html.H1("Análisis de Mortalidad en Colombia (2019)", className="text-center my-4 text-primary fw-bold"),
    dbc.Row([dbc.Col(dcc.Graph(figure=fig_mapa), width=12)], className="mb-4 shadow-sm p-3 bg-body rounded"),
    dbc.Row([dbc.Col(dcc.Graph(figure=fig_lineas), width=6), dbc.Col(dcc.Graph(figure=fig_barras_violencia), width=6)], className="mb-4"),
    dbc.Row([dbc.Col(dcc.Graph(figure=fig_pie_menor), width=6), dbc.Col(dcc.Graph(figure=fig_barras_sexo), width=6)], className="mb-4"),
    dbc.Row([
        dbc.Col([
            html.H5("7. Top 10 Causas de Muerte (CIE-10)", className="text-center mb-3 text-secondary fw-bold"),
            dash_table.DataTable(
                data=df_top_causas.to_dict('records'),
                columns=[{"name": col, "id": col} for col in df_top_causas.columns],
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': '#0d6efd', 'color': 'white', 'fontWeight': 'bold', 'textAlign': 'center'},
                style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '13px'}
            )
        ], width=6),
        dbc.Col(dcc.Graph(figure=fig_histograma_edad), width=6),
    ], className="mb-4 shadow-sm p-3 bg-body rounded")
], fluid=True)

if __name__ == "__main__":
    app.run(debug=False)