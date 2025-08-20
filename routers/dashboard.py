# archivo: routers/dashboard.py

from fastapi import APIRouter, Depends
import crud
from database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats")
def read_dashboard_stats(conn = Depends(get_db)):
    return crud.get_dashboard_stats(conn=conn)

@router.get("/recent-activity")
def read_recent_activity(conn = Depends(get_db)):
    return crud.get_recent_activity(conn=conn)

@router.get("/projects-by-zone")
def read_projects_by_zone(conn = Depends(get_db)):
    return crud.get_projects_by_zone(conn=conn)

@router.get("/units-by-status")
def read_units_by_status(conn = Depends(get_db)):
    return crud.get_units_by_status(conn=conn)