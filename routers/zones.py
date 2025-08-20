# archivo: routers/zones.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
import schemas
import crud
from database import get_db

# Aquí creamos la variable 'router' que main.py está buscando
router = APIRouter(
    prefix="/zones",  # El prefijo se añade a todas las rutas de este archivo
    tags=["Zones"]    # Para agrupar en la documentación automática
)

@router.post("/", response_model=schemas.Zone, status_code=201)
def create_zone(zone: schemas.ZoneCreate, conn = Depends(get_db)):
    return crud.create_zone(conn=conn, zone=zone)

@router.get("/", response_model=List[schemas.Zone])
def read_zones(skip: int = 0, limit: int = 100, conn = Depends(get_db)):
    zones = crud.get_zones(conn=conn, skip=skip, limit=limit)
    return zones

@router.get("/{zone_id}", response_model=schemas.Zone)
def read_zone(zone_id: UUID, conn = Depends(get_db)):
    db_zone = crud.get_zone(conn=conn, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone

# Aquí necesitarás crear las funciones para actualizar (PUT) y borrar (DELETE) en tu archivo crud.py
# @router.put("/{zone_id}", response_model=schemas.Zone)
# def update_zone(...):
#     ...

# @router.delete("/{zone_id}")
# def delete_zone(...):
#     ...
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
import schemas
import crud
from database import get_db

router = APIRouter(
    prefix="/zones",
    tags=["Zones"]
)

@router.post("/", response_model=schemas.Zone, status_code=201)
def create_zone_endpoint(zone: schemas.ZoneCreate, conn = Depends(get_db)):
    return crud.create_zone(conn=conn, zone=zone)

@router.get("/", response_model=List[schemas.Zone])
def read_zones_endpoint(skip: int = 0, limit: int = 100, conn = Depends(get_db)):
    return crud.get_zones(conn=conn, skip=skip, limit=limit)

@router.get("/{zone_id}", response_model=schemas.Zone)
def read_zone_endpoint(zone_id: UUID, conn = Depends(get_db)):
    db_zone = crud.get_zone(conn=conn, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone
