from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers import projects, zones, users, dashboard, units
import uvicorn

app = FastAPI(
    title="Miki.ai API",
    description="La API para la plataforma de gestión de proyectos Miki.ai",
    version="1.0.0"
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers (respetando tu prefijo /api)
app.include_router(projects.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(units.router, prefix="/api")
app.include_router(users.router, prefix="/api")

# Servir tu index.html desde la carpeta templates
@app.get("/")
def read_root():
    return FileResponse("templates/index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
