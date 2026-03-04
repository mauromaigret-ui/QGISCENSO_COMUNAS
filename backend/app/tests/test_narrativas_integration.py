import sys
import os

# Ajustar el path para importar reporting
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.reporting import generar_narrativa, generar_word, DIMENSIONES

def probar_narrativa():
    print("--- Test de Integración: Generador de Narrativas ---\n")
    
    # 1. Test especial de Población Total
    test_poblacion = {
        "Unidad": "personas",
        "Denominador": 1000,
        "Categorias": {
            "Total": {
                "Hombres": 450,
                "Mujeres": 550
            }
        }
    }
    
    resultado_pob = generar_narrativa("Población Total", test_poblacion, 1)
    print("Resultado Población Total:")
    print(resultado_pob)
    print(f"¿Exitoso? {'Sí' if 'De estos, un 55.0% corresponden a mujeres' in resultado_pob else 'No'}\n")
    
    # 2. Test estándar
    test_comun = {
        "Unidad": "personas",
        "Denominador": 1000,
        "Categorias": {
            "Cat A": {"Subtotal": 800, "Mujeres": 500, "Hombres": 300},
            "Cat B": {"Subtotal": 200, "Mujeres": 100, "Hombres": 100},
        }
    }
    
    resultado_ext = generar_narrativa("Prueba Estandar", test_comun, 2)
    print("Resultado Otra Variable:")
    print(resultado_ext)
    print(f"¿Exitoso? {'Sí' if 'Tabla 2' in resultado_ext else 'No'}\n")
    print(f"¿Pudo calcular y enviar porcentaje mujeres tope? {'Sí' if test_comun.get('PctMujeresTop1') == 62.5 else 'No'}\n")
    
if __name__ == "__main__":
    probar_narrativa()
