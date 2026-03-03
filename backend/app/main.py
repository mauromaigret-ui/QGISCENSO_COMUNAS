from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api import censo_router

app = FastAPI(
    title="Emulador Censo 2024 API",
    description="API de Alto Rendimiento conectada a DuckDB para Censo 2024",
    version="1.0"
)

# Configurar CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modificar en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(censo_router.router, prefix="/api")

# Montar carpeta de exportaciones estáticas
exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../exports'))
os.makedirs(exports_dir, exist_ok=True)
app.mount("/exports", StaticFiles(directory=exports_dir), name="exports")

# Montar frontend para UI final
frontend_static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/static'))
app.mount("/static", StaticFiles(directory=frontend_static_dir), name="static")

@app.get("/")
def read_root():
    index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/index.html'))
    return FileResponse(index_path)
