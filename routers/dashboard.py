# archivo: routers/dashboard.py

from fastapi import APIRouter, Depends
import crud
from database import get_db

router = APIRouter(
    prefix="/dashboard-stats",
    tags=["Dashboard"]
)

@router.get("/")
def read_dashboard_stats(conn = Depends(get_db)):
    return crud.get_dashboard_stats(conn=conn)