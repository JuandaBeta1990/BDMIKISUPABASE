# database.py
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
import requests

# Cargar .env
load_dotenv()


# =====================================================
#   BASE DE DATOS 1  (POSTGRES / NEON / LOCAL)
# =====================================================

DB1_URL = os.getenv("DB1_URL")


def _connect_postgres(url: str):
    """Conexión directa a PostgreSQL."""
    if not url:
        raise HTTPException(status_code=500, detail="DB1_URL no está configurado")
    try:
        return psycopg2.connect(url, cursor_factory=RealDictCursor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a BD1: {e}")


def get_db1():
    """Dependency para usar en FastAPI → conn = Depends(get_db1)."""
    conn = _connect_postgres(DB1_URL)
    try:
        yield conn
    finally:
        conn.close()


# =====================================================
#   BASE DE DATOS 2  (SUPABASE REST API)
# =====================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")            # ejemplo: https://bqxjbxcmzbftsdefscip.supabase.co
SUPABASE_APIKEY = os.getenv("SUPABASE_APIKEY")      # apikey completa
SUPABASE_BEARER = os.getenv("SUPABASE_BEARER")      # normalmente es igual a la apikey

# Aviso opcional
if not SUPABASE_URL or not SUPABASE_APIKEY or not SUPABASE_BEARER:
    print("Advertencia: Variables de Supabase no configuradas correctamente")


def supabase_get(table: str, params: dict = None):
    """
    Cliente GET genérico para leer una tabla de Supabase vía REST.
    Ejemplo:
        supabase_get("historial_conversaciones_diarias")
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}"

    headers = {
        "apikey": SUPABASE_APIKEY,
        "Authorization": f"Bearer {SUPABASE_BEARER}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando Supabase: {e}")


def get_supabase():
    """
    Dependency para FastAPI. Uso típico:
        conn = Depends(get_supabase)
        rows = conn("tabla")
    """
    def _client(table: str, params: dict = None):
        return supabase_get(table, params)

    return _client
