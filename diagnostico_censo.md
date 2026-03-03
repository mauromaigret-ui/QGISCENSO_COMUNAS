# Plan Maestro y Guía Multi-Prompt: Emulador App Censo 2024

Este documento define la arquitectura, diagnóstico y los **prompts secuenciales (fases)** para construir la aplicación emuladora del Censo 2024.

---

## Directriz Transversal y Crítica

**RESPETO ABSOLUTO POR LOS DATOS:** En todas y cada una de las fases descritas a continuación, el código generado debe garantizar que no se pierda, modifique ni altere ningún valor original presente en los CSV (`personas_censo2024.csv`, `viviendas_censo2024.csv`, `hogares_censo2024.csv`) ni en el diccionario oficial (`diccionario_variables_censo2024.xlsx`). Toda cruce de datos, filtrado o agrupación debe ser estrictamente validada contra los conteos y universos del diccionario original.

---

## 1. Análisis y Situación Actual

* **Origen:** App local (FastAPI + HTML/JS) que procesaba Excel.
* **Nuevos Datos:** 3 archivos CSV de gran volumen (más de 3.2 GB y 32 millones de filas) más un Diccionario Excel complejo.
* **El Reto:** Filtrar interactivamente por comuna sin agotar la RAM, manteniendo la lógica compleja original de agrupación por Temas/Subtemas y la generación estructurada de reportes Word/Excel **con descripciones narrativas dinámicas**.

---

## 2. Ejecución Multi-Prompt (Fases de Desarrollo)

Para iniciar el desarrollo, debes proporcionar a la IA el siguiente prompt correspondiente a cada fase, una vez que la fase anterior haya finalizado y pasado su test.

### FASE 1: Optimización de Datos (ETL) y Validación Estricta
**Prompt a usar:**
> "Iniciemos la Fase 1 del Plan Maestro del Censo 2024. Crea un script Python estricto (`etl_censo.py`) que lea los archivos CSV de Personas, Viviendas y Hogares, junto con el Diccionario de Variables. Debes consolidar esta información en una base de datos local optimizada (DuckDB). El script *debe* contener rutinas automatizadas de 'Sanity Check' al finalizar, que sumen los totales de registros en DuckDB y los comparen matemáticamente con los CSV originales y el Diccionario para garantizar 100% de fidelidad de datos. No asumas tipos de datos incompletos. Genera también la lógica para exportar fácilmente las tablas de Regiones y Comunas para el frontend."

**Test de Fase 1:** El script finaliza mostrando por terminal que las sumas de DuckDB coinciden exactamente con las filas del CSV original y logrando tiempos de consulta (ej. `SELECT COUNT(*) FROM personas WHERE comuna = X`) en milisegundos.

---

### FASE 2: Backend (FastAPI) y Reglas de Agrupación (Group Rules)
**Prompt a usar:**
> "Iniciemos la Fase 2. Construye el backend en FastAPI. Implementa la conexión a DuckDB creada en la Fase 1. Luego, extrae y adapta la lógica del archivo `group_rules.py` original, pero ahora **basado estrictamente en las variables comprobables del Diccionario** (para las entidades Vivienda, Hogar y Persona respectivamente). Debes crear endpoints que devuelvan JSONs con estas agrupaciones ya calculadas (denominadores, subtotales y porcentajes), filtradas de manera instantánea por el ID de la comuna recibida en el request. Mantén la fidelidad estricta al diccionario."

**Test de Fase 2:** Utilizar `curl` o Swagger (`/docs`) para consultar una comuna específica y obtener un JSON instantáneo (< 1 segundo) que contenga la estructura correcta agrupada y sin errores matemáticos en los porcentajes.

---

### FASE 3: Motor de Reportes (Excel y Word Narrativo)
**Prompt a usar:**
> "Iniciemos la Fase 3. Implementa los servicios de exportación (`reporting.py`). Crea el endpoint que reciba el JSON agrupado de la Fase 2 y genere dos archivos:
> 1. Un Excel (`.xlsx`) con pestañas por cada agrupación temática.
> 2. Un Word (`.docx`) consolidado. Para el documento Word, **es indispensable crear un motor de narrativa dinámico**: por cada tabla generada, la IA/lógica debe inyectar un párrafo descriptivo debajo de la tabla que resuma los hallazgos (ej: categoría dominante, porcentajes clave), respetando siempre el diccionario oficial.
> Guarda los archivos generados y devuelve la URL de descarga."

**Test de Fase 3:** Llamar al endpoint de exportación para una comuna. Descargar el DOCX y el XLSX. Se debe verificar visualmente que el Excel tiene las hojas correctas y que el Word contiene tablas bien formateadas intercaladas con párrafos narrativos coherentes y exactos según la tabla que describen.

---

### FASE 4: Interfaz de Usuario (Frontend HTML/JS) y Empaquetado
**Prompt a usar:**
> "Iniciemos la Fase 4 (Final). Actualiza el `index.html`, `styles.css` y `app.js` de la app original. En lugar de pedir subir un Excel, la barra lateral debe tener selectores (dropdowns) jerárquicos: primero Región, luego Comuna. Al seleccionar la Comuna, debe cargar instantáneamente la vista previa de las tablas en el panel central. Agrega botones visibles para 'Exportar a Excel' y 'Exportar Reporte DOCX (con narrativa)'. Finalmente, regenera el archivo `run_local.sh`, el entorno virtual y actualiza `requirements.txt` con `duckdb`, `fastapi`, `python-docx` y demás librerías para que la app se ejecute con doble clic."

**Test de Fase 4:** Abrir `http://localhost:8000`, verificar que al elegir una comuna se muestran los datos al instante, y que los botones de exportación descargan los archivos generados en la Fase 3 correctamente.
