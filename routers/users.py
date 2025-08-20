
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
import schemas
import crud
from database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=schemas.User, status_code=201)
def create_user_endpoint(user: schemas.UserCreate, conn = Depends(get_db)):
    return crud.create_user(conn=conn, user=user)

@router.get("/", response_model=List[schemas.User])
def read_users_endpoint(skip: int = 0, limit: int = 100, role: str = "", conn = Depends(get_db)):
    return crud.get_users(conn=conn, skip=skip, limit=limit, role_filter=role)

@router.get("/{user_id}", response_model=schemas.User)
def read_user_endpoint(user_id: UUID, conn = Depends(get_db)):
    db_user = crud.get_user(conn=conn, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
def update_user_endpoint(user_id: UUID, user: schemas.UserUpdate, conn = Depends(get_db)):
    db_user = crud.update_user(conn=conn, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}")
def delete_user_endpoint(user_id: UUID, conn = Depends(get_db)):
    result = crud.delete_user(conn=conn, user_id=user_id)
    if result == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
