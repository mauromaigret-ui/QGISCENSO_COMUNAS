import random

def generar_frase_nodeclarado(pct_nodeclarado: float, unidad: str, config: dict) -> str:
    """
    Genera una frase de advertencia sobre el porcentaje de datos "No declarado" 
    en una variable censal, ajustando la intensidad según el nivel de omisión.

    Identifica tres rangos basados en la configuración:
    - Leve (<= umbral_leve): No se genera frase (retorna string vacío).
    - Medio (> umbral_leve y <= umbral_alto): Advertencia simple.
    - Alto (> umbral_alto): Advertencia fuerte sobre el impacto en la lectura.

    Args:
        pct_nodeclarado (float): Porcentaje de 'No respuesta' + 'No declarado'.
        unidad (str): Unidad de análisis ('personas', 'hogares', 'viviendas').
        config (dict): Diccionario de configuración con umbrales.

    Returns:
        str: Frase de advertencia generada aleatoriamente o string vacío.
    """
    umbral_leve = config.get("umbral_nodecl_leve", 5)
    umbral_alto = config.get("umbral_nodecl_alto", 20)

    if pct_nodeclarado <= umbral_leve:
        return ""
    
    elif umbral_leve < pct_nodeclarado <= umbral_alto:
        frases_mediano = [
            f"Un {pct_nodeclarado:.1f}% de {unidad} no declaró información para esta variable.",
            f"Cabe señalar que el {pct_nodeclarado:.1f}% no presenta declaración en esta pregunta."
        ]
        return random.choice(frases_mediano)
        
    else:
        # pct_nodeclarado > umbral_alto
        frases_alto = [
            f"Es relevante considerar que el {pct_nodeclarado:.1f}% de {unidad} no declaró respuesta, por lo que los porcentajes reflejan solo a quienes efectivamente respondieron.",
            f"Debe tenerse presente que un {pct_nodeclarado:.1f}% de los registros carece de declaración en esta variable, lo cual incide en la lectura de las proporciones."
        ]
        return random.choice(frases_alto)

if __name__ == "__main__":
    config_test = {"umbral_nodecl_leve": 5, "umbral_nodecl_alto": 20}

    print("--- Tests de generar_frase_nodeclarado ---\n")

    # Test 1: Bajo (0.0%)
    r1 = generar_frase_nodeclarado(0.0, "personas", config_test)
    print(f"Test 1 (Bajo - 0.0%): '{r1}'")
    print(f"¿Correcto? {'Sí' if r1 == '' else 'No'}\n")

    # Test 2: Leve/Medio (12.0%)
    r2 = generar_frase_nodeclarado(12.0, "hogares", config_test)
    print(f"Test 2 (Medio - 12.0%): {r2}")
    print(f"¿Correcto? {'Sí' if '12.0' in r2 and ('no declaró' in r2 or 'no presenta' in r2) else 'No'}\n")

    # Test 3: Alto (23.3%)
    r3 = generar_frase_nodeclarado(23.3, "viviendas", config_test)
    print(f"Test 3 (Alto - 23.3%): {r3}")
    print(f"¿Correcto? {'Sí' if '23.3' in r3 and ('reflejan solo a quienes' in r3 or 'incide en la lectura' in r3) else 'No'}\n")

    # Test 4: Muy alto (70.3%)
    r4 = generar_frase_nodeclarado(70.3, "personas", config_test)
    print(f"Test 4 (Muy alto - 70.3%): {r4}")
    print(f"¿Correcto? {'Sí' if '70.3' in r4 and ('reflejan solo a quienes' in r4 or 'incide en la lectura' in r4) else 'No'}\n")

    # Test 5: Borde exacto 5.0%
    r5 = generar_frase_nodeclarado(5.0, "personas", config_test)
    print(f"Test 5 (Borde - 5.0%): '{r5}'")
    print(f"¿Correcto? {'Sí' if r5 == '' else 'No'}\n")
