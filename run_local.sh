#!/bin/bash

# ==============================================================================
# Lanzador de la Aplicación del Censo 2024
# Este script crea un entorno virtual, instala las dependencias y lanza la UI.
# ==============================================================================

echo "----------------------------------------------------"
echo " Iniciando Emulador Censo 2024 - Fase 4 "
echo "----------------------------------------------------"

# Navegar al directorio donde se encuentra este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 1. Preparar Entorno Virtual
echo "Verificando el entorno virtual (venv)..."
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# 2. Activar e Instalar Dependencias
echo "Activando entorno virtual..."
source venv/bin/activate

echo "Verificando requerimientos..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt > /dev/null 2>&1

# 3. Lanzar FastAPI
echo "Iniciando servidor backend (FastAPI + DuckDB)..."
# Matar el puerto si estuviese siendo usado previamente
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Corremos uvicorn en el background
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
PID_UVICORN=$!

# Esperar unos segundos a que inicie
sleep 3

# 4. Abrir la UI en el navegador local
echo "Abriendo aplicación en el navegador..."
URL="http://127.0.0.1:8000/"

if which xdg-open > /dev/null
then
  xdg-open "$URL"
elif which gnome-open > /dev/null
then
  gnome-open "$URL"
elif which open > /dev/null
then
  open "$URL"
else
  echo "=> No se pudo abrir automáticamente. Por favor ingresa a $URL en tu navegador."
fi

echo "----------------------------------------------------"
echo "Aplicación corriendo... (El frontend está en el navegador)"
echo "Presione CTRL+C para detener el servidor de la aplicación."

# Mantener vivo el proceso principal para poder cerrarlo fácilmente
wait $PID_UVICORN
