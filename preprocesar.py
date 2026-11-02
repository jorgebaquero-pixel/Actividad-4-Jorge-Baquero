import os
import pandas as pd

# ---------------------------------------------------------
# A. CARGA DE BASES DE DATOS CRUDAS
# ---------------------------------------------------------
print("Cargando archivos de datos...")

df_nofetal = pd.read_excel("NoFetal2019.xlsx")
df_divipola = pd.read_excel("Divipola_CE_.xlsx")
df_causas = pd.read_excel("CodigosDeMuerte.xlsx")

# Crear carpeta de salida
os.makedirs("data", exist_ok=True)

# Normalizar códigos DANE como texto con ceros a la izquierda
df_nofetal["COD_DEPARTAMENTO"] = (
    df_nofetal["COD_DEPARTAMENTO"].astype(str).str.split(".").str[0].str.zfill(2)
)
df_nofetal["COD_DANE"] = (
    df_nofetal["COD_DANE"].astype(str).str.split(".").str[0].str.zfill(5)
)

df_divipola["COD_DEPARTAMENTO"] = (
    df_divipola["COD_DEPARTAMENTO"].astype(str).str.split(".").str[0].str.zfill(2)
)
df_divipola["COD_DANE"] = (
    df_divipola["COD_DANE"].astype(str).str.split(".").str[0].str.zfill(5)
)

# Catálogo único de departamentos
divipola_deptos = df_divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates()

# ---------------------------------------------------------
# B. GENERACIÓN DE LOS ARCHIVOS RESUMIDOS
# ---------------------------------------------------------

# 1. MAPA: Muertes por Departamento
print("Procesando gráfico 1: Mapa por departamento...")
df_mapa = (
    df_nofetal.groupby("COD_DEPARTAMENTO")
    .size()
    .reset_index(name="TOTAL_MUERTES")
)
df_mapa = pd.merge(df_mapa, divipola_deptos, on="COD_DEPARTAMENTO", how="inner")
df_mapa.to_csv("data/muertes_departamento.csv", index=False)

# 2. GRÁFICO DE LÍNEAS: Evolución Mensual
print("Procesando gráfico 2: Tendencia mensual...")
meses_map = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
df_meses = df_nofetal.groupby("MES").size().reset_index(name="TOTAL_MUERTES")
df_meses["NOMBRE_MES"] = df_meses["MES"].map(meses_map)
df_meses.to_csv("data/muertes_mes.csv", index=False)

# 3. GRÁFICO DE BARRAS: Top 5 Ciudades más violentas (Homicidios)
print("Procesando gráfico 3: Top 5 homicidios...")
homicidios = df_nofetal[
    (df_nofetal["MANERA_MUERTE"].astype(str).str.contains("Homicidio", case=False, na=False))
    | (df_nofetal["COD_MUERTE"].astype(str).str.startswith("X95"))
]
top_violentas = (
    homicidios.groupby("COD_DANE")
    .size()
    .reset_index(name="TOTAL_HOMICIDIOS")
)
top_violentas = pd.merge(
    top_violentas,
    df_divipola[["COD_DANE", "MUNICIPIO", "DEPARTAMENTO"]].drop_duplicates(),
    on="COD_DANE",
    how="inner",
)
top_violentas = top_violentas.sort_values(by="TOTAL_HOMICIDIOS", ascending=False).head(5)
top_violentas.to_csv("data/top5_violentas.csv", index=False)

# 4. GRÁFICO CIRCULAR: 10 Ciudades con menor mortalidad
print("Procesando gráfico 4: Top 10 menor mortalidad...")
mortalidad_muni = (
    df_nofetal.groupby("COD_DANE")
    .size()
    .reset_index(name="TOTAL_MUERTES")
)
mortalidad_muni = pd.merge(
    mortalidad_muni,
    df_divipola[["COD_DANE", "MUNICIPIO"]].drop_duplicates(),
    on="COD_DANE",
    how="inner",
)
top10_menor = mortalidad_muni.sort_values(by="TOTAL_MUERTES", ascending=True).head(10)
top10_menor.to_csv("data/top10_menor_mortalidad.csv", index=False)

# 5. TABLA INTERACTIVA: Top 10 Causas de Muerte (CIE-10)
print("Procesando gráfico 5: Top 10 causas de muerte...")

# A. Limpieza de espacios en blanco
df_causas.columns = df_causas.columns.astype(str).str.strip()
df_nofetal["COD_MUERTE"] = df_nofetal["COD_MUERTE"].astype(str).str.strip()

# Identificar columnas con tolerancia a variaciones de nombre
cols_causas = list(df_causas.columns)
col_codigo_cie = next(
    (c for c in cols_causas if any(k in c.lower() for k in ["cód", "cod", "cie"])),
    cols_causas[0]
)
col_desc_cie = next(
    (c for c in cols_causas if any(k in c.lower() for k in ["desc", "nom", "causa"]) and c != col_codigo_cie),
    cols_causas[1] if len(cols_causas) > 1 else cols_causas[0]
)

df_causas[col_codigo_cie] = df_causas[col_codigo_cie].astype(str).str.strip()

# B. Agrupar y contar total de defunciones por causa
top_causas = (
    df_nofetal.groupby("COD_MUERTE")
    .size()
    .reset_index(name="TOTAL_CASOS")
)

# C. Cruzar con el catálogo CIE-10 (eliminando duplicados para no inflar conteos)
catalogo_cie = df_causas[[col_codigo_cie, col_desc_cie]].drop_duplicates(subset=[col_codigo_cie])

top_causas = pd.merge(
    top_causas,
    catalogo_cie,
    left_on="COD_MUERTE",
    right_on=col_codigo_cie,
    how="left"
)

# D. Renombrar y seleccionar columnas
top_causas = top_causas.rename(
    columns={
        "COD_MUERTE": "Código CIE-10",
        col_desc_cie: "Nombre de la Causa de Muerte",
        "TOTAL_CASOS": "Total de Defunciones",
    }
)

columnas_finales = ["Código CIE-10", "Nombre de la Causa de Muerte", "Total de Defunciones"]
top_causas = top_causas[columnas_finales].copy()

# E. Tratar nulos, ordenar y extraer el Top 10
top_causas["Nombre de la Causa de Muerte"] = top_causas["Nombre de la Causa de Muerte"].fillna("Descripción no especificada")
top_causas = top_causas.sort_values(by="Total de Defunciones", ascending=False).head(10)

# F. Guardar archivo CSV
top_causas.to_csv("data/top10_causas.csv", index=False)
print("Top 10 causas actualizado con éxito en data/top10_causas.csv")
# 6. BARRAS APILADAS: Comparación por Sexo y Departamento
print("Procesando gráfico 6: Mortalidad por sexo y departamento...")
df_sexo = (
    df_nofetal.groupby(["COD_DEPARTAMENTO", "SEXO"])
    .size()
    .reset_index(name="TOTAL_MUERTES")
)
sexo_labels = {1: "Hombre", 2: "Mujer", 3: "Indeterminado"}
df_sexo["SEXO_NOMBRE"] = df_sexo["SEXO"].map(sexo_labels).fillna("Sin información")
df_sexo = pd.merge(df_sexo, divipola_deptos, on="COD_DEPARTAMENTO", how="inner")
df_sexo.to_csv("data/muertes_sexo_depto.csv", index=False)

# 7. HISTOGRAMA: Categorización por GRUPO_EDAD1
print("Procesando gráfico 7: Distribución por grupos de edad...")

def clasificar_rango_edad(grupo):
    try:
        g = int(grupo)
    except (ValueError, TypeError):
        return "10. Edad desconocida"

    if g in range(1, 8):
        return "1. Mortalidad infantil (< 1 año)"
    elif g in [8, 9]:
        return "2. Primera infancia (1-4 años)"
    elif g == 10:
        return "3. Niñez (5-14 años)"
    elif g == 11:
        return "4. Adolescencia (15-19 años)"
    elif g in [12, 13]:
        return "5. Juventud (20-29 años)"
    elif g in range(14, 17):
        return "6. Adultez temprana (30-44 años)"
    elif g in range(17, 20):
        return "7. Adultez intermedia (45-59 años)"
    elif g in range(20, 25):
        return "8. Vejez (60-84 años)"
    elif 25 <= g <= 28:
        return "9. Longevidad (85+ años)"
    else:
        return "10. Edad desconocida"

df_nofetal["RANGO_EDAD"] = df_nofetal["GRUPO_EDAD1"].apply(clasificar_rango_edad)
df_edad = (
    df_nofetal.groupby("RANGO_EDAD")
    .size()
    .reset_index(name="TOTAL_MUERTES")
)
df_edad = df_edad.sort_values(by="RANGO_EDAD")
df_edad.to_csv("data/muertes_edad.csv", index=False)

print("\n¡Proceso finalizado con éxito! Todos los archivos CSV han sido generados en la carpeta 'data/'.")