import os
import pandas as pd

print("Iniciando preprocesamiento de datos...")
os.makedirs("data", exist_ok=True)

# ---------------------------------------------------------
# 1. CARGA DE ARCHIVOS
# ---------------------------------------------------------
print("Cargando hojas de cálculo...")
df_nofetal = pd.read_excel("NoFetal2019.xlsx")
df_causas = pd.read_excel("CodigosDeMuerte.xlsx")

# Cargar Hoja3 de Divipola o la primera hoja si no existe ese nombre exacto
try:
    df_divipola_geo = pd.read_excel("Divipola_CE_.xlsx", sheet_name="Hoja3")
except Exception:
    df_divipola_geo = pd.read_excel("Divipola_CE_.xlsx")

# ---------------------------------------------------------
# 2. LIMPIEZA Y NORMALIZACIÓN DE GEOGRAFÍA Y COORDENADAS
# ---------------------------------------------------------
cols_divipola = list(df_divipola_geo.columns)

# Búsqueda tolerante de columnas en Divipola
col_lat = next((c for c in cols_divipola if "lat" in c.lower()), None)
col_lon = next((c for c in cols_divipola if any(k in c.lower() for k in ["lon", "long"])), None)
col_depto_div = next((c for c in cols_divipola if "dep" in c.lower()), None)
col_muni_cod = next((c for c in cols_divipola if any(k in c.lower() for k in ["cód", "cod"])), None)
col_muni_nom = next((c for c in cols_divipola if any(k in c.lower() for k in ["nom", "muni"])), None)

# Conversión segura de coordenadas numéricas
if col_lat and col_lon:
    df_divipola_geo["LATITUD"] = (
        df_divipola_geo[col_lat].astype(str).str.replace(",", ".", regex=False).str.strip()
    )
    df_divipola_geo["LONGITUD"] = (
        df_divipola_geo[col_lon].astype(str).str.replace(",", ".", regex=False).str.strip()
    )
    df_divipola_geo["LATITUD"] = pd.to_numeric(df_divipola_geo["LATITUD"], errors="coerce")
    df_divipola_geo["LONGITUD"] = pd.to_numeric(df_divipola_geo["LONGITUD"], errors="coerce")
    
    depto_geo = (
        df_divipola_geo.groupby(col_depto_div)[["LATITUD", "LONGITUD"]]
        .mean()
        .reset_index()
        .rename(columns={col_depto_div: "DEPARTAMENTO", "LATITUD": "Latitud", "LONGITUD": "Longitud"})
    )
    depto_geo["DEPARTAMENTO"] = depto_geo["DEPARTAMENTO"].astype(str).str.strip().str.upper()
else:
    depto_geo = pd.DataFrame(columns=["DEPARTAMENTO", "Latitud", "Longitud"])

# Normalizar códigos de departamento a dos caracteres
df_nofetal["COD_DEPARTAMENTO"] = (
    df_nofetal["COD_DEPARTAMENTO"]
    .astype(str)
    .str.split(".")
    .str[0]
    .str.strip()
    .str.zfill(2)
)

deptos_nombres = {
    "05": "ANTIOQUIA", "08": "ATLÁNTICO", "11": "BOGOTÁ, D.C.", "13": "BOLÍVAR",
    "15": "BOYACÁ", "17": "CALDAS", "18": "CAQUETÁ", "19": "CAUCA", "20": "CESAR",
    "23": "CÓRDOBA", "25": "CUNDINAMARCA", "27": "CHOCÓ", "41": "HUILA",
    "44": "LA GUAJIRA", "47": "MAGDALENA", "50": "META", "52": "NARIÑO",
    "54": "NORTE DE SANTANDER", "63": "QUINDÍO", "66": "RISARALDA", "68": "SANTANDER",
    "70": "SUCRE", "73": "TOLIMA", "76": "VALLE DEL CAUCA", "81": "ARAUCA",
    "85": "CASANARE", "86": "PUTUMAYO", "88": "ARCHIPIÉLAGO DE SAN ANDRÉS",
    "91": "AMAZONAS", "94": "GUAINÍA", "95": "GUAVIARE", "97": "VAUPÉS", "99": "VICHADA"
}
df_nofetal["DEPARTAMENTO"] = df_nofetal["COD_DEPARTAMENTO"].map(deptos_nombres)

# ---------------------------------------------------------
# G1. MAPA: TOTAL DE MUERTES POR DEPARTAMENTO
# ---------------------------------------------------------
print("1. Procesando Mapa de Departamentos...")
df_mapa = df_nofetal.groupby("DEPARTAMENTO").size().reset_index(name="TOTAL_MUERTES")

if not depto_geo.empty:
    df_mapa = pd.merge(df_mapa, depto_geo, on="DEPARTAMENTO", how="left")

df_mapa.to_csv("data/muertes_departamento.csv", index=False)

# ---------------------------------------------------------
# G2. EVOLUCIÓN MENSUAL
# ---------------------------------------------------------
print("2. Procesando Evolución Mensual...")
meses_map = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
df_nofetal["MES"] = pd.to_numeric(df_nofetal["MES"], errors="coerce")
df_meses = df_nofetal.dropna(subset=["MES"]).groupby("MES").size().reset_index(name="TOTAL_MUERTES")
df_meses["NOMBRE_MES"] = df_meses["MES"].astype(int).map(meses_map)
df_meses = df_meses.sort_values(by="MES")
df_meses.to_csv("data/muertes_mes.csv", index=False)

# ---------------------------------------------------------
# G3 Y G4. MUNICIPIOS: HOMICIDIOS Y MENOR MORTALIDAD
# ---------------------------------------------------------
print("3 y 4. Procesando Municipios...")

# Detectar columna de código de municipio/DANE
col_muni_cod = next(
    (c for c in df_divipola_geo.columns if str(c).upper() in ["COD_DANE", "CODIGO", "CÓDIGO", "COD_MUNICIPIO", "COD_MPIO"]),
    next((c for c in df_divipola_geo.columns if any(k in str(c).lower() for k in ["dane", "cód", "cod"])), df_divipola_geo.columns[0])
)

# Detectar columna de nombre de municipio
col_muni_nom = next(
    (c for c in df_divipola_geo.columns if str(c).upper() in ["MUNICIPIO", "NOMBRE", "NOMBRE_MUNICIPIO", "NOM_MPIO"]),
    next((c for c in df_divipola_geo.columns if any(k in str(c).lower() for k in ["muni", "nom"]) and c != col_muni_cod), df_divipola_geo.columns[1])
)

print(f"   -> Usando para municipios: Código='{col_muni_cod}', Nombre='{col_muni_nom}'")

df_divipola_muni = df_divipola_geo[[col_muni_cod, col_muni_nom]].dropna().drop_duplicates().copy()
df_divipola_muni["COD_DANE"] = (
    df_divipola_muni[col_muni_cod]
    .astype(str)
    .str.split(".")
    .str[0]
    .str.strip()
    .str.zfill(5)
)
df_divipola_muni["MUNICIPIO"] = df_divipola_muni[col_muni_nom].astype(str).str.strip()

# Código y nombre de departamento a partir del código DANE (los primeros 2 dígitos)
df_divipola_muni["COD_DEPARTAMENTO"] = df_divipola_muni["COD_DANE"].str[:2]
df_divipola_muni["DEPARTAMENTO"] = df_divipola_muni["COD_DEPARTAMENTO"].map(deptos_nombres).fillna("OTRO")

# Normalizar COD_DANE en NoFetal2019
col_dane_nofetal = "COD_DANE" if "COD_DANE" in df_nofetal.columns else next(
    (c for c in df_nofetal.columns if any(k in str(c).lower() for k in ["dane", "mpio", "municipio"])), df_nofetal.columns[0]
)

df_nofetal["COD_DANE"] = (
    df_nofetal[col_dane_nofetal]
    .astype(str)
    .str.split(".")
    .str[0]
    .str.strip()
    .str.zfill(5)
)

# Top 5 homicidios
col_manera = next((c for c in df_nofetal.columns if "manera" in str(c).lower()), None)
filtro_manera = df_nofetal[col_manera].astype(str).str.contains("Homicidio", case=False, na=False) if col_manera else False
filtro_cie = df_nofetal["COD_MUERTE"].astype(str).str.upper().str.startswith("X95")

homicidios = df_nofetal[filtro_manera | filtro_cie]
top_violentas = homicidios.groupby("COD_DANE").size().reset_index(name="TOTAL_HOMICIDIOS")
top_violentas = pd.merge(top_violentas, df_divipola_muni[["COD_DANE", "MUNICIPIO", "DEPARTAMENTO"]], on="COD_DANE", how="inner")
top_violentas = top_violentas.sort_values(by="TOTAL_HOMICIDIOS", ascending=False).head(5)
top_violentas.to_csv("data/top5_violentas.csv", index=False)

# Top 10 menor mortalidad
mortalidad_muni = df_nofetal.groupby("COD_DANE").size().reset_index(name="TOTAL_MUERTES")
mortalidad_muni = pd.merge(mortalidad_muni, df_divipola_muni[["COD_DANE", "MUNICIPIO", "DEPARTAMENTO"]], on="COD_DANE", how="inner")
top10_menor = mortalidad_muni.sort_values(by="TOTAL_MUERTES", ascending=True).head(10)
top10_menor.to_csv("data/top10_menor_mortalidad.csv", index=False)


# ---------------------------------------------------------
# G5. TABLA: TOP 10 CAUSAS DE MUERTE CIE-10
# ---------------------------------------------------------
print("5. Procesando Top 10 Causas de Muerte...")
causas_dict = {}

# Detectar columnas en catálogo CIE-10
cols_cie = list(df_causas.columns)
c3_col = next((c for c in cols_cie if "tres" in c.lower() and "cód" in c.lower()), None)
d3_col = next((c for c in cols_cie if "tres" in c.lower() and "desc" in c.lower()), None)
c4_col = next((c for c in cols_cie if "cuatro" in c.lower() and "cód" in c.lower()), None)
d4_col = next((c for c in cols_cie if "cuatro" in c.lower() and "desc" in c.lower()), None)

if c3_col and d3_col:
    for _, row in df_causas[[c3_col, d3_col]].dropna().iterrows():
        cod = str(row[c3_col]).replace(".", "").strip().upper()
        causas_dict[cod] = str(row[d3_col]).strip()

if c4_col and d4_col:
    for _, row in df_causas[[c4_col, d4_col]].dropna().iterrows():
        cod = str(row[c4_col]).replace(".", "").strip().upper()
        causas_dict[cod] = str(row[d4_col]).strip()

df_nofetal["COD_MUERTE_CLEAN"] = (
    df_nofetal["COD_MUERTE"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .str.strip()
    .str.upper()
)

def buscar_descripcion_cie10(codigo):
    if codigo in causas_dict:
        return causas_dict[codigo]
    elif codigo[:3] in causas_dict:
        return causas_dict[codigo[:3]]
    return f"Causa {codigo}"

top_causas = df_nofetal.groupby("COD_MUERTE_CLEAN").size().reset_index(name="Total de Defunciones")
top_causas["Nombre de la Causa de Muerte"] = top_causas["COD_MUERTE_CLEAN"].apply(buscar_descripcion_cie10)
top_causas = top_causas.rename(columns={"COD_MUERTE_CLEAN": "Código CIE-10"})
top_causas = top_causas[["Código CIE-10", "Nombre de la Causa de Muerte", "Total de Defunciones"]]
top_causas = top_causas.sort_values(by="Total de Defunciones", ascending=False).head(10)
top_causas.to_csv("data/top10_causas.csv", index=False)

# ---------------------------------------------------------
# G6. BARRAS APILADAS: SEXO Y DEPARTAMENTO
# ---------------------------------------------------------
print("6. Procesando Mortalidad por Sexo...")
df_sexo = df_nofetal.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="TOTAL_MUERTES")
df_sexo["SEXO_NOMBRE"] = df_sexo["SEXO"].map({1: "Hombre", 2: "Mujer", "1": "Hombre", "2": "Mujer"}).fillna("Indeterminado")
df_sexo.dropna(subset=["DEPARTAMENTO"]).to_csv("data/muertes_sexo_depto.csv", index=False)

# ---------------------------------------------------------
# G7. HISTOGRAMA: RANGOS DE EDAD (GRUPO_EDAD1)
# ---------------------------------------------------------
print("7. Procesando Rangos de Edad...")
def clasificar_rango(val):
    try:
        grupo = int(float(val))
    except (ValueError, TypeError):
        return "10. Edad desconocida"
        
    if grupo in [1, 2]:
        return "1. Mortalidad infantil (1-11 meses)"
    elif grupo in [3, 4]:
        return "2. Primera infancia (1-4 años)"
    elif grupo in [5, 6]:
        return "3. Niñez (5-14 años)"
    elif grupo in [7, 8]:
        return "4. Adolescencia y Juventud (15-24 años)"
    elif grupo in list(range(9, 12)):
        return "5. Juventud y Adultez temprana (25-39 años)"
    elif grupo in list(range(12, 15)):
        return "6. Adultez intermedia (40-54 años)"
    elif grupo in list(range(15, 20)):
        return "7. Vejez (55-79 años)"
    elif grupo in list(range(20, 24)):
        return "8. Longevidad (80+ años)"
    else:
        return "10. Edad desconocida"

df_nofetal["RANGO_EDAD"] = df_nofetal["GRUPO_EDAD1"].apply(clasificar_rango)
df_edad = df_nofetal.groupby("RANGO_EDAD").size().reset_index(name="TOTAL_MUERTES")
df_edad = df_edad.sort_values(by="RANGO_EDAD")
df_edad.to_csv("data/muertes_edad.csv", index=False)

print("\nPreprocesamiento finalizado con éxito. Todos los archivos CSV se encuentran en la carpeta 'data/'.")