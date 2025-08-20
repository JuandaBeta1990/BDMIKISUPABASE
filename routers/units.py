
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
import schemas
import crud
from database import get_db

router = APIRouter(
    prefix="/units",
    tags=["Units"]
)

@router.post("/", response_model=schemas.Unit, status_code=201)
def create_unit_endpoint(unit: schemas.UnitCreate, conn = Depends(get_db)):
    return crud.create_unit(conn=conn, unit=unit)

@router.get("/project/{project_id}", response_model=List[schemas.Unit])
def read_units_by_project_endpoint(project_id: UUID, conn = Depends(get_db)):
    return crud.get_units_by_project(conn=conn, project_id=project_id)

@router.get("/{unit_id}", response_model=schemas.Unit)
def read_unit_endpoint(unit_id: UUID, conn = Depends(get_db)):
    db_unit = crud.get_unit(conn=conn, unit_id=unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return db_unit

@router.put("/{unit_id}", response_model=schemas.Unit)
def update_unit_endpoint(unit_id: UUID, unit: schemas.UnitUpdate, conn = Depends(get_db)):
    db_unit = crud.get_unit(conn=conn, unit_id=unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    return crud.update_unit(conn=conn, unit_id=unit_id, unit=unit)

@router.delete("/{unit_id}")
def delete_unit_endpoint(unit_id: UUID, conn = Depends(get_db)):
    db_unit = crud.get_unit(conn=conn, unit_id=unit_id)
    if db_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    deleted_unit = crud.delete_unit(conn=conn, unit_id=unit_id)
    if deleted_unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return {"message": "Unit deleted successfully"}
