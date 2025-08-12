# archivo: main.py (Versión final y limpia)

from fastapi import FastAPI
from fastapi.responses import FileResponse
from routers import projects, zones
from routers import dashboard
from routers import units

app = FastAPI(
    title="Miki.ai API",
    description="La API para la plataforma de gestión de proyectos Miki.ai",
    version="1.0.0"
)

# Incluir los routers en la aplicación principal
app.include_router(projects.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(units.router, prefix="/api")

# Servir el Frontend
@app.get("/")
def read_root():
    return FileResponse('index.html')