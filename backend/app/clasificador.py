def clasificar_variable(datos: dict) -> dict:
    """
    Clasifica una variable censal según su distribución de datos.
    
    Args:
        datos (dict): Un diccionario contenedor con 'Unidad', 'Denominador' 
                      y un sub-diccionario 'Categorias' con frecuencias.
                      
    Returns:
        dict: Diccionario que contiene:
            - tipo (str): La clasificación de la variable.
            - pct_nodeclarado (float): Porcentaje combinado de no respuesta.
            - flag_alta_no_respuesta (bool): True si pct_nodeclarado > 30.
            - cats_sustantivas (list): Lista de tuplas (nombre, frec, pct).
            - n_cats_sustantivas (int): Cantidad de categorías sustantivas.
            - top_1_pct (float): Porcentaje de la categoría más frecuente.
    """
    denominador = datos.get("Denominador", 1)
    if denominador == 0:
        denominador = 1  # Prevenir división por cero
        
    categorias = datos.get("Categorias", {})
    
    # 1. Calcular pct_nodeclarado
    freq_no_respuesta_raw = categorias.get("No respuesta", 0)
    freq_no_respuesta = freq_no_respuesta_raw.get("Subtotal", 0) if isinstance(freq_no_respuesta_raw, dict) else freq_no_respuesta_raw
    
    freq_no_declarado_raw = categorias.get("No declarado", 0)
    freq_no_declarado = freq_no_declarado_raw.get("Subtotal", 0) if isinstance(freq_no_declarado_raw, dict) else freq_no_declarado_raw
    
    total_no_decl = freq_no_respuesta + freq_no_declarado
    
    pct_nodeclarado = round((total_no_decl / denominador) * 100, 1)
    flag_alta_no_respuesta = pct_nodeclarado > 30.0
    
    # 2. Filtrar categorías sustantivas
    cats_sustantivas = []
    for nombre, freq_raw in categorias.items():
        if nombre not in ["No respuesta", "No declarado", "Total", "Ignorado"]:
            # Compatibilidad: si el dato es un diccionario, la frecuencia está en "Subtotal"
            freq = freq_raw.get("Subtotal", 0) if isinstance(freq_raw, dict) else freq_raw
            pct = round((freq / denominador) * 100, 1) if denominador > 0 else 0
            cats_sustantivas.append((nombre, freq, pct))
            
    # Ordenar descendente por frecuencia
    cats_sustantivas.sort(key=lambda x: x[1], reverse=True)
    
    n_cats_sustantivas = len(cats_sustantivas)
    top_1_pct = cats_sustantivas[0][2] if n_cats_sustantivas > 0 else 0.0
    suma_pct_sustantivas = sum(cat[2] for cat in cats_sustantivas)
    
    # 3. Clasificar según reglas
    # Nota: Si evaluamos estrictamente en orden a, b, c, d, e, el Test 4 ("EXHAUSTIVA")
    # se clasificaría como "DOMINANCIA_CLARA" ya que su top_1_pct es 65.7 >= 50.
    # Por lo tanto, para que el Test 4 pase exitosamente con "EXHAUSTIVA", la regla 'd'
    # debe tener mayor prioridad (evaluarse antes) que la regla 'c'.
    
    nombres_limpios = {cat[0].strip().lower() for cat in cats_sustantivas}
    
    if n_cats_sustantivas == 2 and nombres_limpios == {"sí", "no"}:
        tipo = "BINARIA"
    elif top_1_pct >= 90.0:
        tipo = "DOMINANCIA_EXTREMA"
    elif suma_pct_sustantivas >= 99.0:
        # Se movió esta regla antes que DOMINANCIA_CLARA para satisfacer el Test 4
        tipo = "EXHAUSTIVA"
    elif top_1_pct >= 50.0:
        tipo = "DOMINANCIA_CLARA"
    else:
        tipo = "MULTICATEGORIA"

    return {
        "tipo": tipo,
        "pct_nodeclarado": pct_nodeclarado,
        "flag_alta_no_respuesta": flag_alta_no_respuesta,
        "cats_sustantivas": cats_sustantivas,
        "n_cats_sustantivas": n_cats_sustantivas,
        "top_1_pct": top_1_pct
    }

if __name__ == "__main__":
    datos_test1 = {
        "Unidad": "personas",
        "Denominador": 54222,
        "Categorias": {
            "No respuesta": 351,
            "Sí": 16678,
            "No": 37193,
        }
    }

    datos_test2 = {
        "Unidad": "hogares",
        "Denominador": 18778,
        "Categorias": {
            "No respuesta": 1,
            "Gas": 18191,
            "Parafina o petróleo": 8,
            "Leña": 166,
            "Pellet": 1,
            "Carbón": 2,
            "Electricidad": 153,
            "Energía solar (ej. cocina u horno solar)": 3,
            "No utiliza fuente de energía o combustible para cocinar": 105,
            "No declarado": 148,
        }
    }

    datos_test3 = {
        "Unidad": "viviendas",
        "Denominador": 23540,
        "Categorias": {
            "No respuesta": 5,
            "Red pública": 15584,
            "Pozo o noria": 223,
            "Camión Aljibe": 1382,
            "Río, vertiente, estero, canal, lago, agua lluvia, etc": 856,
            "No declarado": 5490,
        }
    }

    datos_test4 = {
        "Unidad": "personas",
        "Denominador": 54222,
        "Categorias": {
            "0-14": 10541,
            "15-64": 35631,
            "65 y más años": 8050,
        }
    }

    datos_test5 = {
        "Unidad": "personas",
        "Denominador": 54222,
        "Categorias": {
            "No respuesta": 182,
            "Casado/a": 11264,
            "Conviviente o pareja sin acuerdo de unión civil": 7903,
            "Conviviente civil (con acuerdo de unión civil)": 405,
            "Anulado/a": 23,
            "Separado/a": 1310,
            "Divorciado/a": 975,
            "Viudo/a": 2185,
            "Soltero/a": 19434,
            "No declarado": 10541,
        }
    }

    print("--- Test 1 (BINARIA) ---")
    res1 = clasificar_variable(datos_test1)
    print(f"Tipo: {res1['tipo']} (Esperado: BINARIA)")
    print(f"pct_nodeclarado: {res1['pct_nodeclarado']}")
    print(f"flag: {res1['flag_alta_no_respuesta']}")
    print(f"top_1_pct: {res1['top_1_pct']}\n")

    print("--- Test 2 (DOMINANCIA_EXTREMA) ---")
    res2 = clasificar_variable(datos_test2)
    print(f"Tipo: {res2['tipo']} (Esperado: DOMINANCIA_EXTREMA)")
    print(f"top_1_pct: {res2['top_1_pct']}\n")

    print("--- Test 3 (DOMINANCIA_CLARA) ---")
    res3 = clasificar_variable(datos_test3)
    print(f"Tipo: {res3['tipo']} (Esperado: DOMINANCIA_CLARA)")
    print(f"pct_nodeclarado: {res3['pct_nodeclarado']}")
    print(f"flag: {res3['flag_alta_no_respuesta']}")
    print(f"top_1_pct: {res3['top_1_pct']}\n")

    print("--- Test 4 (EXHAUSTIVA) ---")
    res4 = clasificar_variable(datos_test4)
    print(f"Tipo: {res4['tipo']} (Esperado: EXHAUSTIVA)")
    print(f"pct_nodeclarado: {res4['pct_nodeclarado']}")
    print(f"Suma gatos: {sum(c[2] for c in res4['cats_sustantivas'])}%\n")

    print("--- Test 5 (MULTICATEGORIA) ---")
    res5 = clasificar_variable(datos_test5)
    print(f"Tipo: {res5['tipo']} (Esperado: MULTICATEGORIA)")
    print(f"top_1_pct: {res5['top_1_pct']}")
