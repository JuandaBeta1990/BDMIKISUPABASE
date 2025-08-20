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