import random

def generar_frase_resto(pct_restante: float, unidad: str) -> str:
    """
    Genera una frase sobre el porcentaje restante (categorías no mencionadas),
    siempre y cuando este porcentaje sea significativo (> 1%).

    Args:
        pct_restante (float): Porcentaje acumulado de categorías no mencionadas.
        unidad (str): Unidad de análisis ('personas', 'hogares', 'viviendas').

    Returns:
        str: Frase descriptiva generada aleatoriamente si pct_restante > 1.0, 
             de lo contrario retorna un string vacío.
    """
    if pct_restante <= 1.0:
        return ""

    frases = [
        f"El {pct_restante:.1f}% restante se distribuye entre categorías de menor frecuencia.",
        f"Las categorías restantes suman un {pct_restante:.1f}% en conjunto.",
        f"El resto de las opciones representa el {pct_restante:.1f}% de {unidad}."
    ]
    return random.choice(frases)

def generar_ref_tabla(num_tabla: int) -> str:
    """
    Genera una frase de referencia cruzada a la tabla detallada.

    Args:
        num_tabla (int): Número identificador de la tabla mostrada en el reporte.

    Returns:
        str: Frase aleatoria que cita la tabla.
    """
    frases = [
        "La tabla a continuación, presenta la distribución completa.",
        "Ver la siguiente tabla para el detalle.",
        "El desglose detallado se encuentra en la tabla a continuación.",
        "La próxima tabla contiene el desglose por categoría."
    ]
    return random.choice(frases)

if __name__ == "__main__":
    print("--- Tests de generar_frase_resto ---\n")

    # Test 1: resto significativo
    r1 = generar_frase_resto(4.6, "viviendas")
    print(f"Test 1 (Significativo - 4.6%): {r1}")
    print(f"¿Correcto? {'Sí' if '4.6' in r1 else 'No'}\n")

    # Test 2: resto insignificante
    r2 = generar_frase_resto(0.8, "personas")
    print(f"Test 2 (Insignificante - 0.8%): '{r2}'")
    print(f"¿Correcto? {'Sí' if r2 == '' else 'No'}\n")

    # Test 3: borde exacto 1.0
    r3 = generar_frase_resto(1.0, "hogares")
    print(f"Test 3 (Borde - 1.0%): '{r3}'")
    print(f"¿Correcto? {'Sí' if r3 == '' else 'No'}\n")

    print("--- Tests de generar_ref_tabla ---\n")

    # Test 4: tabla 18 (se ignora número)
    r4 = generar_ref_tabla(18)
    print(f"Test abstract sin número: {r4}")
    print(f"¿Correcto? {'Sí' if 'tabla' in r4.lower() else 'No'}\n")

