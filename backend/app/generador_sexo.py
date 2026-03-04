import random

def generar_frase_sexo(pct_mujeres: float, config: dict) -> str:
    """
    Genera una frase sobre composición por sexo cuando la distribución
    es significativamente desigual, basada en umbrales de configuración.

    Si no hay datos de sexo (None) o la distribución es paritaria (dentro
    de los umbrales de paridad inferior y superior), retorna string vacío.

    Args:
        pct_mujeres (float): Porcentaje de mujeres en la categoría principal.
        config (dict): Diccionario de configuración con umbrales de decisión.

    Returns:
        str: Frase descriptiva generada aleatoriamente o string vacío.
    """
    if pct_mujeres is None:
        return ""

    umbral_destacable = config.get("umbral_sexo_destacable", 58)
    # Límite inferior para considerar mayoría masculina = 100 - umbral femenino
    limite_masculino = 100 - umbral_destacable

    if pct_mujeres >= umbral_destacable:
        frases_fem = [
            f"En la categoría principal se observa una composición mayoritariamente femenina ({pct_mujeres:.1f}% mujeres).",
            f"Dentro del grupo predominante, las mujeres representan el {pct_mujeres:.1f}%.",
            f"La categoría principal muestra una mayor presencia femenina ({pct_mujeres:.1f}%)."
        ]
        return random.choice(frases_fem)

    elif pct_mujeres <= limite_masculino:
        pct_hombres = 100 - pct_mujeres
        frases_masc = [
            f"La categoría principal presenta una composición mayoritariamente masculina ({pct_hombres:.1f}% hombres).",
            f"En el grupo predominante, los hombres alcanzan el {pct_hombres:.1f}%.",
            f"Se observa una mayor presencia masculina en la categoría principal ({pct_hombres:.1f}% hombres)."
        ]
        return random.choice(frases_masc)

    else:
        # Entre 43 y 57 inclusive (zona paritaria)
        return ""


if __name__ == "__main__":
    config_test = {
        "umbral_sexo_destacable": 58,
        "umbral_sexo_paritario_sup": 57,
        "umbral_sexo_paritario_inf": 43,
    }

    print("--- Tests de generar_frase_sexo ---\n")

    # Test 1: Predominancia femenina
    r1 = generar_frase_sexo(59.3, config_test)
    print(f"Test 1 (59.3%): {r1}")
    print(f"¿Correcto? {'Sí' if '59.3' in r1 and ('femenina' in r1 or 'mujeres' in r1) else 'No'}\n")

    # Test 2: Predominancia masculina
    r2 = generar_frase_sexo(40.4, config_test)
    print(f"Test 2 (40.4%): {r2}")
    print(f"¿Correcto? {'Sí' if '59.6' in r2 and ('masculina' in r2 or 'hombres' in r2) else 'No'}\n")

    # Test 3: Paritario
    r3 = generar_frase_sexo(50.8, config_test)
    print(f"Test 3 (50.8%): '{r3}'")
    print(f"¿Correcto? {'Sí' if r3 == '' else 'No'}\n")

    # Test 4: Sin desglose
    r4 = generar_frase_sexo(None, config_test)
    print(f"Test 4 (None): '{r4}'")
    print(f"¿Correcto? {'Sí' if r4 == '' else 'No'}\n")

    # Test 5: Borde exacto 58%
    r5 = generar_frase_sexo(58.0, config_test)
    print(f"Test 5 (58.0%): {r5}")
    print(f"¿Correcto? {'Sí' if '58.0' in r5 and ('femenina' in r5 or 'mujeres' in r5) else 'No'}\n")
