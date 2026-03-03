import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.services.group_rules import calcular_todas_las_reglas, VARIABLES_CENSO

router = APIRouter()

class SeleccionVariables(BaseModel):
    variables_seleccionadas: Optional[List[str]] = None

@router.get("/variables")
def get_variables_disponibles():
    try:
        # Devuelve las variables estructuradas pero planas
        lista_vars = ["Poblacion Total"] # Siempre disponible
        for entidad, vars_dict in VARIABLES_CENSO.items():
            for v in vars_dict:
                lista_vars.append(v['desc'])
        return {"variables": lista_vars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regiones")
def get_regiones():
    try:
        con = get_db()
        query = """
        SELECT "Código territorial", "Territorio" 
        FROM codigos_territoriales 
        WHERE "División Política Administrativa" = 'Región'
        ORDER BY "Código territorial"
        """
        df = con.execute(query).df()
        regiones = [{"id": str(row["Código territorial"]), "nombre": str(row["Territorio"])} for _, row in df.iterrows()]
        return {"regiones": regiones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comunas/{region_id}")
def get_comunas(region_id: str):
    try:
        con = get_db()
        query = f"""
        SELECT DISTINCT comuna
        FROM viviendas
        WHERE region = '{region_id}'
        ORDER BY comuna
        """
        df = con.execute(query).df()
        
        nombres_query = """
        SELECT "Código territorial", "Territorio" 
        FROM codigos_territoriales 
        WHERE "División Política Administrativa" = 'Comuna'
        """
        df_nombres = con.execute(nombres_query).df()
        nombres_map = {str(row["Código territorial"]): str(row["Territorio"]) for _, row in df_nombres.iterrows()}
        
        comunas = []
        for _, row in df.iterrows():
            c_id = str(row["comuna"])
            comunas.append({
                "id": c_id,
                "nombre": nombres_map.get(c_id, f"Comuna {c_id}")
            })
            
        return {"comunas": comunas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datos_censo/{comuna_id}")
def get_datos_censo(comuna_id: str, seleccion: SeleccionVariables):
    try:
        data = calcular_todas_las_reglas(comuna_id, seleccion.variables_seleccionadas)
        return {"comuna_id": comuna_id, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from datetime import datetime
from app.services.reporting import generar_excel, generar_word

@router.post("/exportar/{comuna_id}")
def exportar_reporte(comuna_id: str, seleccion: SeleccionVariables):
    try:
        con = get_db()
        query_nombres = f"""
        SELECT 
            (SELECT "Territorio" FROM codigos_territoriales WHERE "Código territorial" = '{comuna_id}') as comuna_nom,
            (SELECT "Territorio" FROM codigos_territoriales WHERE "Código territorial" = (SELECT region FROM viviendas WHERE comuna = '{comuna_id}' LIMIT 1)) as region_nom
        """
        row = con.execute(query_nombres).fetchone()
        comuna_nombre = row[0] if row and row[0] else comuna_id
        region_nombre = row[1] if row and row[1] else "Region"

        data = calcular_todas_las_reglas(comuna_id, seleccion.variables_seleccionadas)

        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        excel_path = generar_excel(comuna_nombre, region_nombre, data, timestamp_str)
        word_path = generar_word(comuna_nombre, region_nombre, data, timestamp_str)

        import urllib.parse
        return {
            "mensaje": "Reportes generados exitosamente",
            "comuna": comuna_nombre,
            "region": region_nombre,
            "excel_url": f"/exports/{urllib.parse.quote(os.path.basename(excel_path))}",
            "word_url": f"/exports/{urllib.parse.quote(os.path.basename(word_path))}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

