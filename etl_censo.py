import duckdb
import pandas as pd
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_etl():
    base_dir = '/Users/mauriciomaigret/Documents/Proyectos QGIS/Censo 2024 - Comunas y Región/Docs/'
    db_path = '/Users/mauriciomaigret/Documents/Proyectos QGIS/Censo 2024 - Comunas y Región/censo2024.duckdb'
    
    # Archivos
    csv_viviendas = os.path.join(base_dir, 'Bases de Datos - Microdatos', 'viviendas_censo2024.csv')
    csv_hogares = os.path.join(base_dir, 'Bases de Datos - Microdatos', 'hogares_censo2024.csv')
    csv_personas = os.path.join(base_dir, 'Bases de Datos - Microdatos', 'personas_censo2024.csv')
    excel_diccionario = os.path.join(base_dir, 'Dicionario', 'diccionario_variables_censo2024.xlsx')

    # Remove existing db if script is re-run (optional, for idempotency)
    if os.path.exists(db_path):
        os.remove(db_path)
        logging.info(f"Removed existing database at {db_path}")

    # Connect to DuckDB
    con = duckdb.connect(db_path)
    logging.info("Connected to DuckDB.")

    # 1. Cargar CSVs a DuckDB
    # Utilizamos all_varchar=1 para leer todo como texto y evitar pérdidas de datos por tipos mal inferidos
    read_csv_options = "delim=';', header=True, auto_detect=True, sample_size=-1, all_varchar=True"
    
    logging.info("Loading viviendas...")
    con.execute(f"CREATE TABLE viviendas AS SELECT * FROM read_csv('{csv_viviendas}', {read_csv_options})")
    
    logging.info("Loading hogares...")
    con.execute(f"CREATE TABLE hogares AS SELECT * FROM read_csv('{csv_hogares}', {read_csv_options})")
    
    logging.info("Loading personas...")
    con.execute(f"CREATE TABLE personas AS SELECT * FROM read_csv('{csv_personas}', {read_csv_options})")

    # 2. Procesar el Diccionario para obtener conteos esperados y códigos territoriales
    logging.info("Processing dictionary...")
    xl = pd.ExcelFile(excel_diccionario)
    
    # Diccionarios de conteos esperados (segun el Excel)
    expected_counts = {}
    
    # Extraer conteo de viviendas
    df_viviendas_dict = pd.read_excel(excel_diccionario, sheet_name='tabla_viviendas')
    expected_counts['viviendas'] = df_viviendas_dict['Conteo'].iloc[0]

    # Extraer conteo de hogares
    df_hogares_dict = pd.read_excel(excel_diccionario, sheet_name='tabla_hogares')
    expected_counts['hogares'] = df_hogares_dict['Conteo'].iloc[0]

    # Extraer conteo de personas
    df_personas_dict = pd.read_excel(excel_diccionario, sheet_name='tabla_personas')
    expected_counts['personas'] = df_personas_dict['Conteo'].iloc[0]

    # Cargar tabla de códigos territoriales
    df_territorial = pd.read_excel(excel_diccionario, sheet_name='codigos_territoriales')
    # Limpiamos nombres de columnas
    df_territorial.columns = [c.strip() for c in df_territorial.columns]
    
    # Guardar la tabla completa en DuckDB por si se necesita
    con.execute("CREATE TABLE codigos_territoriales AS SELECT * FROM df_territorial")

    # 3. Exportar Regiones y Comunas para el Frontend
    logging.info("Exporting regiones and comunas to CSV for Frontend...")
    
    df_regiones = df_territorial[df_territorial['División Política Administrativa'] == 'Región'].copy()
    df_comunas = df_territorial[df_territorial['División Política Administrativa'] == 'Comuna'].copy()
    
    export_dir = '/Users/mauriciomaigret/Documents/Proyectos QGIS/Censo 2024 - Comunas y Región/export/'
    os.makedirs(export_dir, exist_ok=True)
    
    regiones_path = os.path.join(export_dir, 'regiones.csv')
    comunas_path = os.path.join(export_dir, 'comunas.csv')
    
    df_regiones.to_csv(regiones_path, index=False, sep=';', encoding='utf-8')
    df_comunas.to_csv(comunas_path, index=False, sep=';', encoding='utf-8')
    logging.info(f"Exported regiones ({len(df_regiones)} rows) and comunas ({len(df_comunas)} rows).")

    # 4. Strict Sanity Checks
    logging.info("Executing Strict Sanity Checks...")
    errors = []

    def verify_count(table_name, expected):
        actual = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        if actual != expected:
            errors.append(f"❌ ERROR in {table_name}: Expected {expected} rows, but got {actual}")
        else:
            logging.info(f"✅ OK {table_name}: {actual} rows strictly match the Dictionary.")

    verify_count('viviendas', expected_counts['viviendas'])
    verify_count('hogares', expected_counts['hogares'])
    verify_count('personas', expected_counts['personas'])

    # Optional: We could also verify the row count of the physical CSV file itself, 
    # but since DuckDB read_csv reads the whole file directly, achieving the dictionary
    # expected count means we correctly parsed exactly what is supposed to be there.

    if errors:
        logging.error("SANITY CHECK FAILED:")
        for e in errors:
            logging.error(e)
        sys.exit(1)
    else:
        logging.info("🎉 All Sanity Checks passed successfully. Database is ready.")

    con.close()

if __name__ == '__main__':
    run_etl()
