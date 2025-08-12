# archivo: routers/projects.py (ACTUALIZADO CON 'PUT')

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
import schemas
import crud
from database import get_db

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.post("/", response_model=schemas.ProjectWithZone, status_code=201)
def create_project_endpoint(project: schemas.ProjectCreate, conn = Depends(get_db)):
    return crud.create_project(conn=conn, project=project)

@router.get("/", response_model=List[schemas.ProjectWithZone])
def read_projects_endpoint(skip: int = 0, limit: int = 100, conn = Depends(get_db)):
    return crud.get_projects(conn=conn, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=schemas.ProjectWithZone)
def read_project_endpoint(project_id: UUID, conn = Depends(get_db)):
    db_project = crud.get_project(conn=conn, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

# --- NUEVO ENDPOINT PARA ACTUALIZAR (EDITAR) ---
@router.put("/{project_id}", response_model=schemas.ProjectWithZone)
def update_project_endpoint(project_id: UUID, project: schemas.ProjectUpdate, conn = Depends(get_db)):
    db_project = crud.get_project(conn=conn, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.update_project(conn=conn, project_id=project_id, project=project)