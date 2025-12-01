from fastapi import APIRouter, Depends, HTTPException
from typing import List
import schemas
import crud
from database import get_db1

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Crear usuario
@router.post("/", response_model=schemas.User, status_code=201)
def create_user_endpoint(user: schemas.UserCreate, conn = Depends(get_db1)):
    return crud.create_user(conn=conn, user=user)

# Obtener lista de usuarios
@router.get("/", response_model=List[schemas.User])
def read_users_endpoint(skip: int = 0, limit: int = 100, role: str = "", conn = Depends(get_db1)):
    return crud.get_users(conn=conn, skip=skip, limit=limit, role_filter=role)

# Obtener un usuario por ID
@router.get("/{user_id}", response_model=schemas.User)
def read_user_endpoint(user_id: int, conn = Depends(get_db1)):
    db_user = crud.get_user(conn=conn, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Actualizar usuario
@router.put("/{user_id}", response_model=schemas.User)
def update_user_endpoint(user_id: int, user: schemas.UserUpdate, conn = Depends(get_db1)):
    db_user = crud.update_user(conn=conn, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Eliminar usuario
@router.delete("/{user_id}")
def delete_user_endpoint(user_id: int, conn = Depends(get_db1)):
    result = crud.delete_user(conn=conn, user_id=user_id)
    if result == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
