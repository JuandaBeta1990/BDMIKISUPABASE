from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
import schemas
import crud
from database import get_db1

router = APIRouter(
    prefix="/zones",
    tags=["Zones"]
)

@router.post("/", response_model=schemas.Zone, status_code=201)
def create_zone_endpoint(zone: schemas.ZoneCreate, conn = Depends(get_db1)):
    return crud.create_zone(conn=conn, zone=zone)

@router.get("/", response_model=List[schemas.Zone])
def read_zones_endpoint(skip: int = 0, limit: int = 100, conn = Depends(get_db1)):
    return crud.get_zones(conn=conn, skip=skip, limit=limit)

@router.get("/{zone_id}", response_model=schemas.Zone)
def read_zone_endpoint(zone_id: UUID, conn = Depends(get_db1)):
    db_zone = crud.get_zone(conn=conn, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone

@router.put("/{zone_id}", response_model=schemas.Zone)
def update_zone_endpoint(zone_id: UUID, zone: schemas.ZoneUpdate, conn = Depends(get_db1)):
    db_zone = crud.update_zone(conn=conn, zone_id=zone_id, zone=zone)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone

@router.delete("/{zone_id}")
def delete_zone_endpoint(zone_id: UUID, conn = Depends(get_db1)):
    result = crud.delete_zone(conn=conn, zone_id=zone_id)
    if result == 0:
        raise HTTPException(status_code=404, detail="Zone not found")
    return {"message": "Zone deleted successfully"}

@router.get("/zones")
def list_zones(skip: int = 0, limit: int = 100, conn = Depends(get_db1)):
    return crud.get_zones(conn, skip=skip, limit=limit)

@router.get("/zones/{zone_id}")
def read_zone(zone_id: str, conn = Depends(get_db1)):
    return crud.get_zone(conn, zone_id)