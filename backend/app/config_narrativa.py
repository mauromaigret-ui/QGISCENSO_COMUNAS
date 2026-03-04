"""
Módulo de configuración para la generación de narrativas descriptivas
de datos censales (Censo 2024, Chile).

Contiene umbrales numéricos de decisión y diccionarios de alias
para hacer legibles las categorías largas.
"""

# 1. CONFIG_NARRATIVA
# Umbrales numéricos y configuraciones base para la narrativa.
CONFIG_NARRATIVA = {
    # Umbrales de clasificación de variables
    "umbral_dominancia_extrema": 90,  # % para clasificar como dominancia extrema
    "umbral_dominancia_clara": 50,    # % para clasificar como dominancia clara
    "umbral_multicategoria_top": 5,   # % mínimo para incluir una categoría en el texto

    # Umbrales de mención de sexo
    "umbral_sexo_destacable": 58,     # % mujeres para mencionar predominancia femenina
    "umbral_sexo_paritario_sup": 57,  # límite superior de zona paritaria
    "umbral_sexo_paritario_inf": 43,  # límite inferior de zona paritaria

    # Umbrales de "No declarado"
    "umbral_nodecl_leve": 5,          # % para mención breve
    "umbral_nodecl_alto": 20,         # % para mención prominente

    # Cantidad de categorías a mencionar
    "max_cats_texto": 3,              # para tipo MULTICATEGORIA
    "max_cats_dominancia": 2,         # para tipo DOMINANCIA_CLARA

    # Fuente
    "fuente": "Censo 2024"
}

# 2. ALIAS_CATEGORIAS
# Mapeo de nombres exactos de categorías censales a versiones cortas legibles.
ALIAS_CATEGORIAS = {
    # Materialidad piso
    "Parquet, piso flotante, cerámico, madera, alfombra, flexit, cubrepiso u otro similar; sobre radier o vigas de madera": "revestimiento sobre radier o vigas de madera",

    # Materialidad techo
    "Tejas o tejuelas de arcilla, metálicas, de cemento, de madera, asfálticas o plásticas": "tejas o tejuelas",
    "Planchas metálicas de zinc, cobre, etc": "planchas metálicas (zinc, cobre u otro)",
    "Planchas de fibrocemento tipo pizarreño": "fibrocemento tipo pizarreño",
    "Fonolita o plancha de fieltro embreado": "fonolita o fieltro embreado",
    "Materiales precarios o de desecho: cartón, sacos, trozos de latas o plásticos, etc": "materiales precarios o de desecho",

    # Materialidad paredes
    "Albañilería: bloque de cemento, ladrillo o piedra": "albañilería (bloque, ladrillo o piedra)",
    "Tabique forrado por ambas caras (madera o acero)": "tabique forrado por ambas caras",
    "Tabique sin forro interior (madera u otro)": "tabique sin forro interior",
    "Adobe, barro, pirca, quincha u otro material artesanal": "adobe, barro u otro material artesanal",
    "Materiales precarios o de desecho: cartón, sacos, trozos de latas o plásticos, etc.": "materiales precarios o de desecho",

    # Transporte
    "Transporte público (bus, micro, metro, tren, taxi, colectivo)": "transporte público",
    "Bicicleta (incluye scooter)": "bicicleta o scooter",

    # Servicio higiénico
    "Dentro de la vivienda, conectado a una red de alcantarillado": "WC conectado a alcantarillado (dentro de la vivienda)",
    "Fuera de la vivienda, conectado a una red de alcantarillado": "WC conectado a alcantarillado (fuera de la vivienda)",
    "Conectado a pozo negro (letrina sanitaria o cajón)": "pozo negro o letrina",

    # Agua
    "Río, vertiente, estero, canal, lago, agua lluvia, etc": "fuentes naturales (río, vertiente, etc.)",
    "Con llave dentro de la vivienda": "llave dentro de la vivienda",
    "Con llave dentro del sitio, pero fuera de la vivienda": "llave dentro del sitio (fuera de la vivienda)",

    # Calefacción / cocina
    "No utiliza fuente de energía o combustible para calefaccionar": "no utiliza calefacción",
    "No utiliza fuente de energía o combustible para cocinar": "no utiliza energía para cocinar",
    "Energía solar (ej. cocina u horno solar)": "energía solar",

    # Categoría ocupacional
    "Trabajador/a familiar o personal no remunerado en un negocio de un integrante de su familia": "trabajador/a familiar no remunerado",

    # Estado conyugal
    "Conviviente o pareja sin acuerdo de unión civil": "conviviente sin AUC",
    "Conviviente civil (con acuerdo de unión civil)": "conviviente con AUC",

    # Vivienda
    "Mediagua, mejora, vivienda de emergencia, rancho o choza": "mediagua o vivienda de emergencia",
    "Vivienda tradicional indígena (ruka u otras)": "vivienda tradicional indígena",
    "Móvil (carpa, casa rodante o similar)": "vivienda móvil",
    "Propiedad en sucesión o litigio": "sucesión o litigio",
    "Usufructo: solo uso y goce": "usufructo"
}
