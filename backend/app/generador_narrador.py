import random
import re

# =====================================================================
# IMPORTS DEL SISTEMA (o fallbacks simples para testing standalone)
# =====================================================================
try:
    from app.config_narrativa import CONFIG_NARRATIVA, ALIAS_CATEGORIAS
except ImportError:
    try:
        from config_narrativa import CONFIG_NARRATIVA, ALIAS_CATEGORIAS
    except ImportError:
        CONFIG_NARRATIVA = {"max_cats_texto": 3, "umbral_nodecl_leve": 5, "umbral_nodecl_alto": 20, "umbral_sexo_destacable": 58, "umbral_sexo_paritario_sup": 57, "umbral_sexo_paritario_inf": 43}
        ALIAS_CATEGORIAS = {}

try:
    from app.clasificador import clasificar_variable
except ImportError:
    try:
        from clasificador import clasificar_variable
    except ImportError:
        def clasificar_variable(datos): return {"tipo": "BINARIA", "pct_nodeclarado": 0.0, "cats_sustantivas": [], "n_cats_sustantivas": 0, "top_1_pct": 0.0}

try:
    from app.aplicador_alias import aplicar_alias
except ImportError:
    try:
        from aplicador_alias import aplicar_alias
    except ImportError:
        def aplicar_alias(nombre, alias_dict): return nombre

try:
    from app.generador_sexo import generar_frase_sexo
except ImportError:
    try:
        from generador_sexo import generar_frase_sexo
    except ImportError:
        def generar_frase_sexo(pct, config): return ""

try:
    from app.generador_nodeclarado import generar_frase_nodeclarado
except ImportError:
    try:
        from generador_nodeclarado import generar_frase_nodeclarado
    except ImportError:
        def generar_frase_nodeclarado(pct, un, conf): return ""

try:
    from app.generador_resto_y_ref import generar_frase_resto, generar_ref_tabla
except ImportError:
    try:
        from generador_resto_y_ref import generar_frase_resto, generar_ref_tabla
    except ImportError:
        def generar_frase_resto(pct, un): return ""
        def generar_ref_tabla(num): return ""


# =====================================================================
# ORQUESTADOR
# =====================================================================
def generar_narrativa(titulo: str, datos: dict, num_tabla: int,
                      config: dict = None, alias: dict = None) -> str:
    """
    Genera el párrafo descriptivo final de una variable censal, orquestando
    las funciones modulares previas.

    Args:
        titulo (str): Nombre de la variable (título del gráfico o tabla).
        datos (dict): Diccionario de datos crudos.
        num_tabla (int): ID de la tabla asociada.
        config (dict, opcional): Diccionario de configuración de umbrales.
        alias (dict, opcional): Diccionario de alias de categorías.

    Returns:
        str: Párrafo descriptivo depurado para el reporte Word.
    """
    if config is None:
        config = CONFIG_NARRATIVA
    if alias is None:
        alias = ALIAS_CATEGORIAS

    # PASO 1. Limpiar título
    # Quitar comillas
    titulo_limpio = titulo.replace("'", "").replace('"', "").strip()
    
    # Bajar a minúscula la primera letra SI la segunda letra es minúscula
    # (heurística para no afectar siglas ni nombres propios/ALL CAPS)
    if len(titulo_limpio) > 1 and titulo_limpio[0].isupper() and titulo_limpio[1].islower():
        titulo_limpio = titulo_limpio[0].lower() + titulo_limpio[1:]

    # PASO 2. Clasificar variable
    clasificacion = clasificar_variable(datos)
    tipo = clasificacion["tipo"]
    unidad = datos.get("Unidad", "unidades")
    cats_originales = clasificacion["cats_sustantivas"] # Lista de tuplas: (nombre, frec, pct)
    
    # Variables a extraer
    if not cats_originales:
        return f"No hay datos suficientes para {titulo_limpio}."
        
    # Variables de acceso fácil
    cat1 = aplicar_alias(cats_originales[0][0], alias)
    pct1 = f"{cats_originales[0][2]:.1f}"
    
    cat2 = pct2 = None
    if len(cats_originales) > 1:
        cat2 = aplicar_alias(cats_originales[1][0], alias)
        pct2 = f"{cats_originales[1][2]:.1f}"

    cat3 = pct3 = None
    if len(cats_originales) > 2:
        cat3 = aplicar_alias(cats_originales[2][0], alias)
        pct3 = f"{cats_originales[2][2]:.1f}"

    pct_suma_top = 0.0
    pct_restante_calculado = 0.0
    cuerpo = ""
    frase_resto = ""

    # PASO 3 y 4. Construir cuerpo del texto basado en TIPO
    if tipo == "DOMINANCIA_EXTREMA":
        pct_suma_top = float(pct1)
        # Solo mencionar cat2 si supera el 3% (opcional según requerimiento implícito de dominancia)
        # Las plantillas dadas asumen que se menciona 1 o "resto". 
        pct_resto = round(100.0 - float(pct1), 1)
        
        plantillas = [
            f"Respecto a {titulo_limpio}, {cat1} concentra prácticamente la totalidad de {unidad} ({pct1}%), mientras que las categorías restantes representan en conjunto apenas un {pct_resto}%.",
            f"En cuanto a {titulo_limpio}, se observa una marcada concentración en {cat1}, que agrupa al {pct1}% de {unidad}. Las demás opciones registran frecuencias marginales.",
            f"La variable {titulo_limpio} muestra escasa variabilidad en la comuna: {cat1} alcanza un {pct1}%, con presencia menor del resto de categorías."
        ]
        cuerpo = random.choice(plantillas)
        
    elif tipo == "DOMINANCIA_CLARA":
        pct_suma_top = float(pct1) + (float(pct2) if cat2 else 0.0)
        pct_restante_calculado = sum(c[2] for c in cats_originales[2:]) if cat2 else sum(c[2] for c in cats_originales[1:])
        frase_resto = generar_frase_resto(pct_restante_calculado, unidad)
        
        titulo_mayus = titulo_limpio.capitalize()
        plantillas = [
            f"En relación con {titulo_limpio}, {cat1} representa la mayor proporción con un {pct1}% de {unidad}, seguida de {cat2} ({pct2}%). {frase_resto}",
            f"Para la variable {titulo_limpio}, más de la mitad de {unidad} se concentra en {cat1} ({pct1}%). En segundo lugar se ubica {cat2} con un {pct2}%. {frase_resto}",
            f"{titulo_mayus} presenta una distribución donde {cat1} agrupa al {pct1}%, en tanto que {cat2} alcanza el {pct2}%. {frase_resto}",
            f"Los resultados del Censo 2024 para {titulo_limpio} indican que {cat1} es la opción predominante ({pct1}%), a distancia de {cat2} ({pct2}%). {frase_resto}"
        ]
        cuerpo = random.choice(plantillas)

    elif tipo == "BINARIA":
        # cats_originales tiene ("Sí", frec, pct) y ("No", frec, pct). 
        # Extraemos directamente los pct_si, pct_no (las tuplas están ordenadas desc, así que si != cat1)
        if cats_originales[0][0].lower() == "sí":
            pct_si = pct1
            pct_no = pct2
        else:
            pct_si = pct2
            pct_no = pct1
            
        cat_mayor = cat1.lower()
        cat_menor = cat2.lower()
        pct_mayor = pct1
        pct_menor = pct2
        
        plantillas = [
            f"Respecto a {titulo_limpio}, el {pct_si}% de {unidad} declara que sí, frente a un {pct_no}% que no.",
            f"En la variable {titulo_limpio}, {pct_mayor}% de {unidad} responde {cat_mayor}, mientras que el {pct_menor}% indica {cat_menor}.",
            f"La variable {titulo_limpio} muestra que {pct_mayor}% de {unidad} se inclina por {cat_mayor}, en contraste con un {pct_menor}% que señala {cat_menor}."
        ]
        cuerpo = random.choice(plantillas)
        
    elif tipo == "EXHAUSTIVA":
        # Armar texto "X representa el A%, Y el B% y Z el C%" de todas
        lista_partes = []
        for c in cats_originales:
            alias_c = aplicar_alias(c[0], alias)
            lista_partes.append(f"{alias_c} ({c[2]:.1f}%)")
            
        if len(lista_partes) > 1:
            lista_cats_con_pct = ", ".join(lista_partes[:-1]) + " y " + lista_partes[-1]
        else:
            lista_cats_con_pct = lista_partes[0]
            
        plantillas = [
            f"La distribución de {titulo_limpio} se compone de {lista_cats_con_pct}.",
            f"Respecto a {titulo_limpio}, la distribución se reparte entre {lista_cats_con_pct}, abarcando la totalidad de {unidad}."
        ]
        
        if cat3:
            plantillas.append(f"En cuanto a {titulo_limpio}, {cat1} representa el {pct1}% de {unidad}, {cat2} el {pct2}%, y {cat3} el {pct3}%.")
            
        cuerpo = random.choice(plantillas)
        
    else:  # MULTICATEGORIA
        num_mencionar = config.get("max_cats_texto", 3)
        if cat3 and float(pct3) < 5.0:
            num_mencionar = 2
            
        if num_mencionar >= 3 and cat3:
            pct_restante_calculado = sum(c[2] for c in cats_originales[3:])
            frase_resto = generar_frase_resto(pct_restante_calculado, unidad)
            pct_suma_top = round(float(pct1) + float(pct2) + float(pct3), 1)
            
            plantillas = [
                f"La variable {titulo_limpio} presenta una distribución diversa. La categoría más frecuente es {cat1} ({pct1}%), seguida de {cat2} ({pct2}%) y {cat3} ({pct3}%). {frase_resto}",
                f"En {titulo_limpio}, las categorías con mayor representación son {cat1} ({pct1}%), {cat2} ({pct2}%) y {cat3} ({pct3}%), que en conjunto agrupan al {pct_suma_top}% de {unidad}. {frase_resto}",
                f"Respecto a {titulo_limpio}, destaca {cat1} como la opción más frecuente ({pct1}%), junto con {cat2} ({pct2}%) y {cat3} ({pct3}%). Las demás categorías se distribuyen en proporciones menores. {frase_resto}",
                f"Los datos del Censo 2024 para {titulo_limpio} muestran que {cat1}, {cat2} y {cat3} concentran las mayores frecuencias, con {pct1}%, {pct2}% y {pct3}% respectivamente. {frase_resto}"
            ]
        else: # Solo 2 Cats
            pct_restante_calculado = sum(c[2] for c in cats_originales[2:])
            frase_resto = generar_frase_resto(pct_restante_calculado, unidad)
            pct_suma_top = round(float(pct1) + float(pct2), 1)
            
            plantillas = [
                f"La variable {titulo_limpio} presenta una distribución diversa. La categoría más frecuente es {cat1} ({pct1}%), seguida de {cat2} ({pct2}%). {frase_resto}",
                f"En {titulo_limpio}, las categorías con mayor representación son {cat1} ({pct1}%) y {cat2} ({pct2}%), que en conjunto agrupan al {pct_suma_top}% de {unidad}. {frase_resto}",
                f"Respecto a {titulo_limpio}, destaca {cat1} como la opción más frecuente ({pct1}%), junto con {cat2} ({pct2}%). Las demás categorías se distribuyen en proporciones menores. {frase_resto}",
                f"Los datos del Censo 2024 para {titulo_limpio} muestran que {cat1} y {cat2} concentran las mayores frecuencias, con {pct1}% y {pct2}% respectivamente. {frase_resto}"
            ]
            
        cuerpo = random.choice(plantillas)


    # PASO 5. Generar componentes modulares adicionales
    frase_sexo = generar_frase_sexo(datos.get("PctMujeresTop1"), config)
    frase_nodecl = generar_frase_nodeclarado(clasificacion["pct_nodeclarado"], unidad, config)
    frase_tabla = generar_ref_tabla(num_tabla)

    # PASO 6. Ensamblar
    parrafo = f"{cuerpo} {frase_nodecl} {frase_sexo} {frase_tabla}"
    
    # Limpiador final (quitar espacios dobles, asegurar punto final)
    # 1. Limpiar espacios múltiples a uno
    parrafo = re.sub(r'\s+', ' ', parrafo).strip()
    # 2. Reemplazar '. .' por '.'
    parrafo = parrafo.replace('. .', '.')
    # 3. Capitalizar TODO el párrafo al inicio (cubre "en" -> "En")
    if len(parrafo) > 0:
        parrafo = parrafo[0].upper() + parrafo[1:]
    # 4. Asegurar punto final (sin puntos dobles)
    if not parrafo.endswith('.'):
        parrafo += '.'
    parrafo = parrafo.replace('..', '.')

    return parrafo


# =====================================================================
# SECCIÓN DE PRUEBAS
# =====================================================================
if __name__ == "__main__":
    
    print("\n" + "="*50)
    print("ORQUESTADOR: TESTEO DE CASOS DE USO REALES")
    print("="*50 + "\n")

    # Tests mockeados copiados desde el prompt
    
    # Test 1 — Transporte (MULTICATEGORIA, 70.3% no declarado, sexo masculino)
    test1_titulo = "Medio de transporte principal al trabajo"
    test1_datos = {
        "Unidad": "personas", "Denominador": 54222,
        "Categorias": {
            "No respuesta": 5, "Auto particular": 5092,
            "Transporte público (bus, micro, metro, tren, taxi, colectivo)": 6125,
            "Caminando": 2212, "Bicicleta (incluye scooter)": 205,
            "Motocicleta": 84, "Caballo, lancha o bote": 5, "Otro": 2399,
            "No declarado": 38095,
        },
        "PctMujeresTop1": 40.4,
    }
    
    # Test 2 — Combustible cocinar (DOMINANCIA_EXTREMA, sin desglose sexo)
    test2_titulo = "Combustible para cocinar"
    test2_datos = {
        "Unidad": "hogares", "Denominador": 18778,
        "Categorias": {
            "No respuesta": 1, "Gas": 18191, "Parafina o petróleo": 8,
            "Leña": 166, "Pellet": 1, "Carbón": 2, "Electricidad": 153,
            "Energía solar (ej. cocina u horno solar)": 3,
            "No utiliza fuente de energía o combustible para cocinar": 105,
            "No declarado": 148,
        },
        "PctMujeresTop1": None,
    }

    # Test 3 — Edad en tramos (EXHAUSTIVA, sexo paritario)
    test3_titulo = "Edad en tramos"
    test3_datos = {
        "Unidad": "personas", "Denominador": 54222,
        "Categorias": { "0-14": 10541, "15-64": 35631, "65 y más años": 8050, },
        "PctMujeresTop1": 50.8,
    }

    # Test 4 — Autoidentificación indígena (BINARIA)
    test4_titulo = "Autoiden. pueblo indígena u originario"
    test4_datos = {
        "Unidad": "personas", "Denominador": 54222,
        "Categorias": { "No respuesta": 351, "Sí": 16678, "No": 37193, },
        "PctMujeresTop1": 50.4,
    }

    # Test 5 — Origen del agua (DOMINANCIA_CLARA, 23.3% no declarado)
    test5_titulo = "Origen del agua (Fuente principal)"
    test5_datos = {
        "Unidad": "viviendas", "Denominador": 23540,
        "Categorias": {
            "No respuesta": 5, "Red pública": 15584, "Pozo o noria": 223,
            "Camión Aljibe": 1382,
            "Río, vertiente, estero, canal, lago, agua lluvia, etc": 856,
            "No declarado": 5490,
        },
        "PctMujeresTop1": None,
    }
    
    # Pruebas e informes
    tests = [
        ("TEST 1 (Transporte - Multicategoria, Alto ND, SexMasc)", test1_titulo, test1_datos, 1),
        ("TEST 2 (Cocina - Dom. Extrema, ND leve, SinSexo)", test2_titulo, test2_datos, 23),
        ("TEST 3 (Edad - Exhaustiva, ND nulo, SexParitario)", test3_titulo, test3_datos, 2),
        ("TEST 4 (Indígena - Binaria, ND leve, SexParitario)", test4_titulo, test4_datos, 5),
        ("TEST 5 (Agua - Dom. Clara, ND Alto, SinSexo)", test5_titulo, test5_datos, 18),
    ]
    
    for t_num, (nombre, titulo, datos, tabla) in enumerate(tests, 1):
        print(f"--- {nombre} ---")
        clase = clasificar_variable(datos)
        print(f"1. Tipo: {clase['tipo']} (ND: {clase['pct_nodeclarado']}%, Top1: {clase['top_1_pct']}%)")
        
        texto = generar_narrativa(titulo, datos, tabla)
        print(f"2. Párrafo generado:\n   {texto}")
        
        # Validaciones empíricas
        mayor_falso = "mayoría" in texto.lower() and clase["top_1_pct"] < 50.0
        sexo_incorr = ("femenina" in texto.lower() or "masculina" in texto.lower() or "mujeres" in texto.lower() or "hombres" in texto.lower()) and "PctMujeresTop1" in datos and datos["PctMujeresTop1"] is not None and 43 <= datos["PctMujeresTop1"] <= 57
        no_decl = ("declaró" in texto.lower() or "declaración" in texto.lower())
        no_decl_esperado = clase["pct_nodeclarado"] > 5.0
        ref_tabla = f"Tabla {tabla}" in texto or f"tabla {tabla}" in texto.lower()
        
        print(f"   Checklist:")
        print(f"   [{'✓' if not mayor_falso else '✗'}] Mayoría correcta (falsa mayoría evitada)")
        print(f"   [{'✓' if not sexo_incorr else '✗'}] Sexo paritario ausente correctamente")
        print(f"   [{'✓' if no_decl == no_decl_esperado else '✗'}] Advierte No Declarado s/corresponde ({clase['pct_nodeclarado']}%)")
        print(f"   [{'✓' if ref_tabla else '✗'}] Referencia a Tabla {tabla} presente")
        print("\n")
