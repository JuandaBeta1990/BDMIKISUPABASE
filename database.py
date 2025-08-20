# database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException

# Database configuration
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mikiai")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "password")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")

def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Constructing the connection string from environment variables if DATABASE_URL is not set
        conn_string = f"host='{DATABASE_HOST}' dbname='{DATABASE_NAME}' user='{DATABASE_USER}' password='{DATABASE_PASSWORD}' port='{DATABASE_PORT}'"
        try:
            conn = psycopg2.connect(conn_string)
            return conn
        except psycopg2.OperationalError as e:
            raise HTTPException(status_code=500, detail=f"Error al conectar a la base de datos: {e}")
    else:
        # Using DATABASE_URL if it is set
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
            conn.close()