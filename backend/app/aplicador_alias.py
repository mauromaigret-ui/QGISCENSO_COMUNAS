def aplicar_alias(nombre_categoria: str, alias_dict: dict) -> str:
    """
    Reemplaza nombres largos de categorías censales por versiones cortas.
    
    Limpia el string de entrada (quita espacios extra y comillas simples/dobles)
    antes de buscar en el diccionario. Si la categoría existe en el diccionario,
    retorna su alias. Si no, retorna la categoría original (limpia).

    Args:
        nombre_categoria (str): Nombre original de la categoría.
        alias_dict (dict): Diccionario de mapeo {nombre_original: alias}.

    Returns:
        str: El alias corto si existe en el diccionario;
             de lo contrario, devuelve el nombre original (limpio).
    """
    # 1. Hacer strip() y remover comillas simples y dobles
    nombre_limpio = nombre_categoria.strip().replace("'", "").replace('"', "")
    
    # 2. Retornar el alias si existe, si no, el nombre limpio original
    return alias_dict.get(nombre_limpio, nombre_limpio)


if __name__ == "__main__":
    alias_ejemplo = {
        "Transporte público (bus, micro, metro, tren, taxi, colectivo)": "transporte público",
        "Albañilería: bloque de cemento, ladrillo o piedra": "albañilería (bloque, ladrillo o piedra)",
    }

    print("--- Tests de aplicar_alias ---")

    # Test 1: Con alias
    resultado1 = aplicar_alias("Transporte público (bus, micro, metro, tren, taxi, colectivo)", alias_ejemplo)
    print(f"Test 1:\nResultado: '{resultado1}'\nEsperado: 'transporte público'\n")

    # Test 2: Sin alias (retorna original)
    resultado2 = aplicar_alias("Gas", alias_ejemplo)
    print(f"Test 2:\nResultado: '{resultado2}'\nEsperado: 'Gas'\n")

    # Test 3: Con comillas
    resultado3 = aplicar_alias('"Albañilería: bloque de cemento, ladrillo o piedra"', alias_ejemplo)
    print(f"Test 3:\nResultado: '{resultado3}'\nEsperado: 'albañilería (bloque, ladrillo o piedra)'\n")

    # Test 4: Con espacios extra
    resultado4 = aplicar_alias("  Gas  ", alias_ejemplo)
    print(f"Test 4:\nResultado: '{resultado4}'\nEsperado: 'Gas'\n")
