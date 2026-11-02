import os
import pandas as pd
import numpy as np

print("=== INICIANDO PREPROCESAMIENTO DE DATOS (ACTIVIDAD 4) ===")

# ---------------------------------------------------------
# 1. CARGA SEGURA DE ARCHIVOS ORIGEN
# ---------------------------------------------------------
def cargar_archivo(nombre_base):
    for ext in ['.xlsx', '.csv']:
        archivo = nombre_base + ext
        if os.path.exists(archivo):
            print(f"-> Cargando {archivo}...")
            if ext == '.xlsx':
                return pd.read_excel(archivo, engine="openpyxl")
            else:
                try:
                    return pd.read_csv(archivo, sep=None, engine='python', encoding='utf-8')
                except Exception:
                    return pd.read_csv(archivo, sep=';', encoding='latin-1')
    raise FileNotFoundError(f"No se encontró el archivo {nombre_base} (.xlsx o .csv)")

df_nofetal = cargar_archivo("NoFetal2019")
df_causas = cargar_archivo("CodigosDeMuerte")

# ---------------------------------------------------------
# 2. CATÁLOGO GEOESPACIAL OFICIAL (CENTROIDES DEPARTAMENTOS DE COLOMBIA)
# ---------------------------------------------------------
# Evita depender de hojas corruptas o sin coordenadas en Divipola para el mapa nacional
coords_departamentos = {
    '05': {'DEPARTAMENTO': 'ANTIOQUIA', 'Latitud': 7.0, 'Longitud': -75.5},
    '08': {'DEPARTAMENTO': 'ATLÁNTICO', 'Latitud': 10.7, 'Longitud': -74.9},
    '11': {'DEPARTAMENTO': 'BOGOTÁ, D.C.', 'Latitud': 4.6097, 'Longitud': -74.0817},
    '13': {'DEPARTAMENTO': 'BOLÍVAR', 'Latitud': 9.0, 'Longitud': -74.3},
    '15': {'DEPARTAMENTO': 'BOYACÁ', 'Latitud': 5.5, 'Longitud': -73.0},
    '17': {'DEPARTAMENTO': 'CALDAS', 'Latitud': 5.3, 'Longitud': -75.3},
    '18': {'DEPARTAMENTO': 'CAQUETÁ', 'Latitud': 1.0, 'Longitud': -74.0},
    '19': {'DEPARTAMENTO': 'CAUCA', 'Latitud': 2.5, 'Longitud': -76.8},
    '20': {'DEPARTAMENTO': 'CESAR', 'Latitud': 9.3, 'Longitud': -73.5},
    '23': {'DEPARTAMENTO': 'CÓRDOBA', 'Latitud': 8.3, 'Longitud': -75.6},
    '25': {'DEPARTAMENTO': 'CUNDINAMARCA', 'Latitud': 4.8, 'Longitud': -74.1},
    '27': {'DEPARTAMENTO': 'CHOCÓ', 'Latitud': 5.7, 'Longitud': -76.7},
    '41': {'DEPARTAMENTO': 'HUILA', 'Latitud': 2.5, 'Longitud': -75.6},
    '44': {'DEPARTAMENTO': 'LA GUAJIRA', 'Latitud': 11.5, 'Longitud': -72.9},
    '47': {'DEPARTAMENTO': 'MAGDALENA', 'Latitud': 10.4, 'Longitud': -74.4},
    '50': {'DEPARTAMENTO': 'META', 'Latitud': 3.5, 'Longitud': -73.0},
    '52': {'DEPARTAMENTO': 'NARIÑO', 'Latitud': 1.5, 'Longitud': -77.5},
    '54': {'DEPARTAMENTO': 'NORTE DE SANTANDER', 'Latitud': 8.0, 'Longitud': -73.0},
    '63': {'DEPARTAMENTO': 'QUINDÍO', 'Latitud': 4.4, 'Longitud': -75.7},
    '66': {'DEPARTAMENTO': 'RISARALDA', 'Latitud': 4.9, 'Longitud': -75.8},
    '68': {'DEPARTAMENTO': 'SANTANDER', 'Latitud': 6.8, 'Longitud': -73.4},
    '70': {'DEPARTAMENTO': 'SUCRE', 'Latitud': 9.0, 'Longitud': -75.0},
    '73': {'DEPARTAMENTO': 'TOLIMA', 'Latitud': 4.0, 'Longitud': -75.2},
    '76': {'DEPARTAMENTO': 'VALLE DEL CAUCA', 'Latitud': 3.8, 'Longitud': -76.5},
    '81': {'DEPARTAMENTO': 'ARAUCA', 'Latitud': 6.5, 'Longitud': -71.0},
    '85': {'DEPARTAMENTO': 'CASANARE', 'Latitud': 5.3, 'Longitud': -71.9},
    '86': {'DEPARTAMENTO': 'PUTUMAYO', 'Latitud': 0.5, 'Longitud': -76.5},
    '88': {'DEPARTAMENTO': 'ARCHIPIÉLAGO DE SAN ANDRÉS', 'Latitud': 12.55, 'Longitud': -81.7},
    '91': {'DEPARTAMENTO': 'AMAZONAS', 'Latitud': -1.5, 'Longitud': -71.5},
    '94': {'DEPARTAMENTO': 'GUAINÍA', 'Latitud': 2.5, 'Longitud': -68.5},
    '95': {'DEPARTAMENTO': 'GUAVIARE', 'Latitud': 2.0, 'Longitud': -72.5},
    '97': {'DEPARTAMENTO': 'VAUPÉS', 'Latitud': 0.8, 'Longitud': -70.5},
    '99': {'DEPARTAMENTO': 'VICHADA', 'Latitud': 4.3, 'Longitud': -69.5}
}

df_depto_master = pd.DataFrame.from_dict(coords_departamentos, orient='index').reset_index()
df_depto_master = df_depto_master.rename(columns={'index': 'COD_DEPARTAMENTO'})

# ---------------------------------------------------------
# 3. EXTRACCIÓN Y CATALOGACIÓN DE MUNICIPIOS (DIVIPOLA)
# ---------------------------------------------------------
muni_dict = {}

# Diccionario de respaldo inmediato con las ciudades frecuentes en defunciones
muni_respaldo = {
    '76001': 'CALI', '11001': 'BOGOTÁ, D.C.', '05001': 'MEDELLÍN', '08001': 'BARRANQUILLA',
    '54001': 'CÚCUTA', '68001': 'BUCARAMANGA', '13001': 'CARTAGENA', '66001': 'PEREIRA',
    '73001': 'IBAGUÉ', '41001': 'NEIVA', '52001': 'PASTO', '50001': 'VILLAVICENCIO',
    '17001': 'MANIZALES', '63001': 'ARMENIA', '23001': 'MONTERÍA', '70001': 'SINCELEJO',
    '47001': 'SANTA MARTA', '20001': 'VALLEDUPAR', '27001': 'QUIBDÓ', '19001': 'POPAYÁN',
    '85001': 'YOPAL', '81001': 'ARAUCA', '86001': 'MOCOA', '18001': 'FLORENCIA',
    # Municipios de menor índice reportados
    '97666': 'TARAIRA', '52390': 'LA CRUZ', '50245': 'EL CALVARIO', '27495': 'NÓVITA',
    '68344': 'HIRBA', '13650': 'SAN FERNANDO', '27025': 'ALTO BAUDÓ', '13440': 'MARGARITA',
    '91263': 'EL ENCANTO', '94663': 'MAPIRIPANA'
}
muni_dict.update(muni_respaldo)

# Cargar catálogo de Divipola buscando en todas las hojas disponibles
archivo_div = "Divipola_CE_.xlsx" if os.path.exists("Divipola_CE_.xlsx") else "Divipola_CE_.csv"
try:
    if archivo_div.endswith('.xlsx'):
        xl = pd.ExcelFile(archivo_div, engine="openpyxl")
        for hoja in xl.sheet_names:
            df_h = pd.read_excel(archivo_div, sheet_name=hoja, engine="openpyxl")
            df_h.columns = df_h.columns.astype(str).str.strip().str.upper()
            c_cod = next((c for c in df_h.columns if any(k in c for k in ['COD', 'CÓD'])), None)
            c_nom = next((c for c in df_h.columns if any(k in c for k in ['MUN', 'NOMBRE']) and 'COD' not in c and 'DEP' not in c), None)
            if c_cod and c_nom:
                for _, r in df_h[[c_cod, c_nom]].dropna().iterrows():
                    cod_val = str(r[c_cod]).replace('.0', '').strip().zfill(5)
                    muni_dict[cod_val] = str(r[c_nom]).strip().upper()
    else:
        df_div = pd.read_csv(archivo_div, sep=None, engine='python')
        df_div.columns = df_div.columns.astype(str).str.strip().str.upper()
        c_cod = next((c for c in df_div.columns if any(k in c for k in ['COD', 'CÓD'])), None)
        c_nom = next((c for c in df_div.columns if any(k in c for k in ['MUN', 'NOMBRE']) and 'COD' not in c and 'DEP' not in c), None)
        if c_cod and c_nom:
            for _, r in df_div[[c_cod, c_nom]].dropna().iterrows():
                cod_val = str(r[c_cod]).replace('.0', '').strip().zfill(5)
                muni_dict[cod_val] = str(r[c_nom]).strip().upper()
except Exception as e:
    print(f"-> Nota sobre Divipola: Se utilizó catálogo maestro integrado ({e})")

# ---------------------------------------------------------
# 4. NORMALIZACIÓN DE MICRODATOS (NoFetal2019)
# ---------------------------------------------------------
df_nofetal.columns = df_nofetal.columns.astype(str).str.strip()

col_muni_nofetal = next((c for c in df_nofetal.columns if c.upper() in ['COD_DANE', 'COD_MUNIC', 'COD_MUNICIPIO', 'CODMUN', 'MUNICIPIO']), None)
col_dep_nofetal = next((c for c in df_nofetal.columns if c.upper() in ['COD_DEPARTAMENTO', 'COD_DPTO', 'CODDEP', 'DEPARTAMENTO']), None)

serie_muni = df_nofetal[col_muni_nofetal].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
serie_dep = df_nofetal[col_dep_nofetal].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(2)

if serie_muni.str.len().max() <= 3:
    df_nofetal['COD_DANE'] = serie_dep + serie_muni.str.zfill(3)
else:
    df_nofetal['COD_DANE'] = serie_muni.str.zfill(5)

df_nofetal['COD_DEPARTAMENTO'] = df_nofetal['COD_DANE'].str[:2]
df_nofetal['DEPARTAMENTO'] = df_nofetal['COD_DEPARTAMENTO'].map(lambda c: coords_departamentos.get(c, {}).get('DEPARTAMENTO', 'DESCONOCIDO'))
df_nofetal['MUNICIPIO'] = df_nofetal['COD_DANE'].map(lambda c: muni_dict.get(c, f"Municipio {c}"))

os.makedirs("data", exist_ok=True)

# ---------------------------------------------------------
# 5. GENERACIÓN Y GUARDADO DE LOS 7 ARCHIVOS CSV
# ---------------------------------------------------------

# G1. Mapa por Departamentos con coordenadas 100% garantizadas
print("-> Generando G1 (muertes_departamento.csv)...")
df_mapa = df_nofetal[df_nofetal['DEPARTAMENTO'] != 'DESCONOCIDO'].groupby(['COD_DEPARTAMENTO', 'DEPARTAMENTO']).size().reset_index(name='TOTAL_MUERTES')
df_mapa = pd.merge(df_mapa, df_depto_master[['COD_DEPARTAMENTO', 'Latitud', 'Longitud']], on='COD_DEPARTAMENTO', how='inner')
df_mapa.to_csv("data/muertes_departamento.csv", index=False)
print(f"   [OK] {len(df_mapa)} departamentos georreferenciados exitosamente.")

# G2. Meses
print("-> Generando G2 (muertes_mes.csv)...")
meses_map = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
col_mes = next((c for c in df_nofetal.columns if 'MES' in c.upper()), 'MES')
df_meses = df_nofetal.groupby(col_mes).size().reset_index(name='TOTAL_MUERTES')
df_meses['NOMBRE_MES'] = df_meses[col_mes].map(meses_map)
df_meses.to_csv("data/muertes_mes.csv", index=False)

# G3. Top 5 Violentas (con nombres de ciudad en texto)
print("-> Generando G3 (top5_violentas.csv)...")
col_manera = next((c for c in df_nofetal.columns if 'MANERA' in c.upper()), None)
col_muerte = next((c for c in df_nofetal.columns if 'C_MUERTE' in c.upper() or 'COD_MUERTE' in c.upper()), None)

filtro_homicidios = pd.Series(False, index=df_nofetal.index)
if col_manera:
    filtro_homicidios |= df_nofetal[col_manera].astype(str).str.contains('Homicidio|2', case=False, na=False)
if col_muerte:
    filtro_homicidios |= df_nofetal[col_muerte].astype(str).str.startswith(('X95', 'X9', 'Y0'))

df_homicidios = df_nofetal[filtro_homicidios]
top_violentas = df_homicidios.groupby('MUNICIPIO').size().reset_index(name='TOTAL_HOMICIDIOS')
top_violentas = top_violentas.sort_values(by='TOTAL_HOMICIDIOS', ascending=False).head(5)
top_violentas.to_csv("data/top5_violentas.csv", index=False)
print(f"   [OK] Top 5 municipios detectados: {list(top_violentas['MUNICIPIO'])}")

# G4. Top 10 Menor Mortalidad
print("-> Generando G4 (top10_menor_mortalidad.csv)...")
top10_menor = df_nofetal.groupby('MUNICIPIO').size().reset_index(name='TOTAL_MUERTES')
top10_menor = top10_menor.sort_values(by='TOTAL_MUERTES', ascending=True).head(10)
top10_menor.to_csv("data/top10_menor_mortalidad.csv", index=False)

# ---------------------------------------------------------
# G5. Top 10 Causas de Muerte (CIE-10)
# ---------------------------------------------------------
print("-> Generando G5 (top10_causas.csv)...")

# Catálogo base de respaldo oficial CIE-10 para las causas más prevalentes
causas_dict = {
    'I219': 'Infarto agudo del miocardio, sin otra especificación',
    'I21':  'Infarto agudo del miocardio',
    'J449': 'Enfermedad pulmonar obstructiva crónica, no especificada',
    'J440': 'Enfermedad pulmonar obstructiva crónica con infección aguda respiratoria',
    'J44':  'Otras enfermedades pulmonares obstructivas crónicas',
    'J189': 'Neumonía, no especificada',
    'J18':  'Neumonía, organismo no especificado',
    'C169': 'Tumor maligno del estómago, parte no especificada',
    'C16':  'Tumor maligno del estómago',
    'C349': 'Tumor maligno de los bronquios o del pulmón, parte no especificada',
    'C34':  'Tumor maligno de los bronquios y del pulmón',
    'X954': 'Agresión con disparo de armas de fuego en calles y carreteras',
    'X95':  'Agresión con disparo de otras armas de fuego',
    'C509': 'Tumor maligno de la mama, parte no especificada',
    'C50':  'Tumor maligno de la mama',
    'C61':  'Tumor maligno de la próstata',
    'I10':  'Hipertensión esencial (primaria)',
    'E147': 'Diabetes mellitus no especificada, con complicaciones circulatorias'
}

# Lectura dinámica de todas las columnas del archivo CodigosDeMuerte
for _, row in df_causas.iterrows():
    # Recorrer columnas en pares (código, descripción)
    for i in range(0, len(df_causas.columns) - 1, 2):
        col_c = df_causas.columns[i]
        col_d = df_causas.columns[i + 1]
        c_val = str(row[col_c]).strip().upper().replace('.', '')
        d_val = str(row[col_d]).strip()
        if c_val and c_val not in ['NAN', 'NONE', ''] and d_val and d_val not in ['NAN', 'NONE', '']:
            causas_dict[c_val] = d_val

df_nofetal['COD_MUERTE_CLEAN'] = df_nofetal[col_muerte].astype(str).str.strip().str.upper().str.replace('.', '', regex=False)

def buscar_desc(c):
    if c in causas_dict:
        return causas_dict[c]
    if c[:3] in causas_dict:
        return causas_dict[c[:3]]
    return f"Causa {c}"

top_causas = df_nofetal.groupby('COD_MUERTE_CLEAN').size().reset_index(name='Total de Defunciones')
top_causas['Nombre de la Causa de Muerte'] = top_causas['COD_MUERTE_CLEAN'].apply(buscar_desc)
top_causas = top_causas.rename(columns={'COD_MUERTE_CLEAN': 'Código CIE-10'})
top_causas = top_causas[['Código CIE-10', 'Nombre de la Causa de Muerte', 'Total de Defunciones']].sort_values(by='Total de Defunciones', ascending=False).head(10)
top_causas.to_csv("data/top10_causas.csv", index=False)
print("   [OK] Top 10 causas procesadas con sus nombres textuales.")

# G6. Sexo y Departamento
print("-> Generando G6 (muertes_sexo_depto.csv)...")
col_sexo = next((c for c in df_nofetal.columns if 'SEXO' in c.upper()), 'SEXO')
df_sexo = df_nofetal[df_nofetal['DEPARTAMENTO'] != 'DESCONOCIDO'].groupby(['DEPARTAMENTO', col_sexo]).size().reset_index(name='TOTAL_MUERTES')
df_sexo['SEXO_NOMBRE'] = df_sexo[col_sexo].astype(str).replace({'1': 'Hombre', '2': 'Mujer', '1.0': 'Hombre', '2.0': 'Mujer'}).fillna('Otro')
df_sexo.to_csv("data/muertes_sexo_depto.csv", index=False)

# G7. Rangos de Edad
print("-> Generando G7 (muertes_edad.csv)...")
col_edad = next((c for c in df_nofetal.columns if 'GRUPO' in c.upper() or 'EDAD' in c.upper()), None)
def clasificar_rango(val):
    try: g = int(float(val))
    except: return '10. Edad desconocida'
    if g in [1, 2]: return '1. Infantil (1-11 meses)'
    elif g in [3, 4]: return '2. Primera infancia (1-4 años)'
    elif g in [5, 6, 7, 8, 9, 10]: return '3. Niñez (5-14 años)'
    elif g == 11: return '4. Adolescencia (15-19 años)'
    elif g in [12, 13]: return '5. Juventud (20-29 años)'
    elif g in [14, 15, 16]: return '6. Adultez temprana (30-44 años)'
    elif g in [17, 18, 19]: return '7. Adultez intermedia (45-59 años)'
    elif g in [20, 21, 22, 23, 24]: return '8. Vejez (60-84 años)'
    elif g >= 25 and g < 99: return '9. Longevidad (85+ años)'
    return '10. Edad desconocida'

df_nofetal['RANGO_EDAD'] = df_nofetal[col_edad].apply(clasificar_rango)
df_nofetal.groupby('RANGO_EDAD').size().reset_index(name='TOTAL_MUERTES').to_csv("data/muertes_edad.csv", index=False)

print("\n=== ¡PREPROCESAMIENTO COMPLETADO EXITOSAMENTE! ===")
print("Todos los archivos CSV se han generado de forma correcta y limpia en la carpeta 'data/'.")