import os
import json
from app.database import get_db

MAPPING_DICT = {}
mapping_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'diccionario_mapeo.json')
try:
    with open(mapping_path, 'r', encoding='utf-8') as f:
        MAPPING_DICT = json.load(f)
except Exception as e:
    print(f"Advertencia: No se pudo cargar el diccionario de mapeo: {e}")

VARIABLES_CENSO = {
  "viviendas": [
    {"col": "p2_tipo_vivienda", "desc": "Tipo de vivienda particular"},
    {"col": "p3a_estado_ocupacion", "desc": "Estado de ocupación de la vivienda"},
    {"col": "p4a_mat_paredes", "desc": "Material de construcción en las paredes exteriores"},
    {"col": "p4b_mat_techo", "desc": "Material de construcción en la cubierta del techo"},
    {"col": "p4c_mat_piso", "desc": "Material de construcción en el piso"},
    {"col": "p6_fuente_agua", "desc": "Origen del agua (Fuente principal)"},
    {"col": "p7_distrib_agua", "desc": "Sistema de distribución del agua"},
    {"col": "p8_serv_hig", "desc": "Servicio higiénico (WC)"},
    {"col": "p9_fuente_elect", "desc": "Origen de la electricidad"},
    {"col": "p10_basura", "desc": "Medio de eliminación de basura"}
  ],
  "hogares": [
    {"col": "p12_tenencia_viv", "desc": "Tenencia de vivienda"},
    {"col": "p13_comb_cocina", "desc": "Combustible para cocinar"},
    {"col": "p14_comb_calefaccion", "desc": "Combustible para calefaccionar"},
    {"col": "p15d_serv_internet_fija", "desc": "Dispone de internet fija"}
  ],
  "personas": [
    {"col": "edad_quinquenal", "desc": "Edad en tramos"},
    {"col": "p23_est_civil", "desc": "Estado conyugal o civil"},
    {"col": "p28_autoid_pueblo", "desc": "Autoiden. pueblo indígena u originario"},
    {"col": "p28_pueblo_pert", "desc": "A qué pueblo indígena pertenece"},
    {"col": "p29_afrodescendencia_rec", "desc": "Afrodescendencia"},
    {"col": "p31_religion_rec", "desc": "Tiene religión o credo"},
    {"col": "discapacidad", "desc": "Discapacidad"},
    {"col": "escolaridad", "desc": "Años de escolaridad"},
    {"col": "sit_fuerza_trabajo", "desc": "Situación en la fuerza de trabajo"},
    {"col": "p40_cise_rec", "desc": "Categoría ocupacional"},
    {"col": "p45_medio_transporte", "desc": "Medio de transporte principal al trabajo"}
  ]
}

def _calcular_porcentajes(data, total_denominador):
    """Calcula porcentajes para cada subtotal respecto al total."""
    for key in data['Categorias']:
        if total_denominador > 0:
            porcentaje = (data['Categorias'][key]['Subtotal'] / total_denominador) * 100
        else:
            porcentaje = 0
        data['Categorias'][key]['Porcentaje'] = round(porcentaje, 2)
    return data

def get_poblacion_total(comuna_id: str):
    con = get_db()
    query = f"""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN sexo = '1' THEN 1 ELSE 0 END) as hombres,
        SUM(CASE WHEN sexo = '2' THEN 1 ELSE 0 END) as mujeres
    FROM personas 
    WHERE comuna = '{comuna_id}'
    """
    res = con.execute(query).fetchone()
    total = res[0] or 0
    hombres = res[1] or 0
    mujeres = res[2] or 0

    data = {
        "Denominador": total,
        "Unidad": "personas",
        "Categorias": {
            "Total": {"Subtotal": total, "Hombres": hombres, "Mujeres": mujeres}
        }
    }
    return _calcular_porcentajes(data, total)

def _calcular_variable(comuna_id: str, entidad: str, columna: str, desc: str):
    con = get_db()
    
    # Manejar agrupamiento dinámico de edad
    col_seleccion = columna
    if columna == 'edad_quinquenal':
        col_seleccion = "CASE WHEN TRY_CAST(edad AS INTEGER) <= 14 THEN '0-14' WHEN TRY_CAST(edad AS INTEGER) <= 64 THEN '15-64' ELSE '65 y más años' END"
    
    # Manejar variables específicas por entidad
    if entidad == 'personas':
        query = f"""
        SELECT 
            {col_seleccion} as cat,
            COUNT(*) as subtotal,
            SUM(CASE WHEN sexo = '1' THEN 1 ELSE 0 END) as hombres,
            SUM(CASE WHEN sexo = '2' THEN 1 ELSE 0 END) as mujeres
        FROM personas 
        WHERE comuna = '{comuna_id}'
        GROUP BY {col_seleccion}
        ORDER BY TRY_CAST({col_seleccion} AS INTEGER) ASC, {col_seleccion} ASC
        """
        unidad = "personas"
    else:
        query = f"""
        SELECT 
            {col_seleccion} as cat,
            COUNT(*) as subtotal
        FROM {entidad} 
        WHERE comuna = '{comuna_id}'
        GROUP BY {col_seleccion}
        ORDER BY TRY_CAST({col_seleccion} AS INTEGER) ASC, {col_seleccion} ASC
        """
        unidad = entidad

    df = con.execute(query).df()
    total = int(df['subtotal'].sum())
    
    categorias = {}
    # Obtener mapeo de etiquetas para esta columna
    dict_columna = MAPPING_DICT.get(columna, {})

    for _, row in df.iterrows():
        cat_raw = str(row['cat']).strip()
        if cat_raw.endswith('.0'): 
            cat_raw = cat_raw[:-2]

        if cat_raw.lower() in ('nan', 'none', ''):
            cat_label = 'No declarado'
        else:
            cat_label = dict_columna.get(cat_raw, cat_raw)
            # Normalizar "-99" vs "99" si el texto es literal numérico a veces
            if cat_label == cat_raw and cat_raw == "-99" and "99" in dict_columna:
                cat_label = dict_columna.get("99", "No informado")
                
        # Fallback manual para -99 y 99 si no están en diccionario general
        if cat_label in ("-99", "99", 99, -99):
            cat_label = "No informado"
            
        valor_dict = {
            "Subtotal": int(row['subtotal'])
        }
        if entidad == 'personas':
            valor_dict["Hombres"] = int(row['hombres'])
            valor_dict["Mujeres"] = int(row['mujeres'])
            
        # Acumular por si hay duplicados por No Declarados u otros mapeos que converjan
        if cat_label in categorias:
            categorias[cat_label]["Subtotal"] += valor_dict["Subtotal"]
            if entidad == 'personas':
                categorias[cat_label]["Hombres"] += valor_dict["Hombres"]
                categorias[cat_label]["Mujeres"] += valor_dict["Mujeres"]
        else:
            categorias[cat_label] = valor_dict

    data = {
        "Denominador": total,
        "Unidad": unidad,
        "Categorias": categorias
    }
    return _calcular_porcentajes(data, total)


def calcular_todas_las_reglas(comuna_id: str, seleccionadas: list = None) -> dict:
    """Orquesta todas las consultas y devuelve el JSON maestro de la comuna."""
    resultados = {}
    
    # Siempre incluir población total, usando el nuevo nombre
    titulo_pob = "Población Total"
    if not seleccionadas or titulo_pob in seleccionadas:
        resultados[titulo_pob] = get_poblacion_total(comuna_id)
        
    for entidad, vars_list in VARIABLES_CENSO.items():
        for var in vars_list:
            titulo = var['desc']
            if not seleccionadas or titulo in seleccionadas:
                resultados[titulo] = _calcular_variable(comuna_id, entidad, var['col'], var['desc'])

    return resultados
