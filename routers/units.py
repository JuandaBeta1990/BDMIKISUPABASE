# routers/units.py

from fastapi import APIRouter, Depends
import uuid
import crud
import schemas
from database import get_db3

router = APIRouter(prefix="/units", tags=["Units"])

@router.get("/")
def get_units(skip: int = 0, limit: int = 1000, conn=Depends(get_db3)):
    try:
        result = crud.get_all_units(conn, skip, limit)
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error en get_units: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@router.get("/{unit_id}")
def get_unit(unit_id: uuid.UUID, conn=Depends(get_db3)):
    return crud.get_unit(conn, str(unit_id))

@router.get("/project/{project_id}")
def get_units_by_project(project_id: uuid.UUID, conn=Depends(get_db3)):
    return crud.get_units_by_project(conn, str(project_id))

@router.post("/")
def create_unit(unit: schemas.UnitCreate, conn=Depends(get_db3)):
    return crud.create_unit(conn, unit)

@router.patch("/{unit_id}")
def update_unit(unit_id: uuid.UUID, unit: schemas.UnitUpdate, conn=Depends(get_db3)):
    return crud.update_unit(conn, str(unit_id), unit)

@router.delete("/{unit_id}")
def delete_unit(unit_id: uuid.UUID, conn=Depends(get_db3)):
    return crud.delete_unit(conn, str(unit_id))
