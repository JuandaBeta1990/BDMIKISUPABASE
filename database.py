# database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException

def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está configurada.")
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar a la base de datos: {e}")

def get_db():
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    finally:
        if conn:
            conn.close())