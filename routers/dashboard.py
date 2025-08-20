from fastapi import APIRouter, Depends
import crud
from database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats")
def get_dashboard_stats_endpoint(conn = Depends(get_db)):
    return crud.get_dashboard_stats(conn=conn)

@router.get("/recent-activity")
def get_recent_activity_endpoint(limit: int = 10, conn = Depends(get_db)):
    return crud.get_recent_activity(conn=conn, limit=limit)

@router.get("/projects-by-zone")
def get_projects_by_zone_endpoint(conn = Depends(get_db)):
    return crud.get_projects_by_zone(conn=conn)

@router.get("/units-by-status")
def get_units_by_status_endpoint(conn = Depends(get_db)):
    return crud.get_units_by_status(conn=conn)