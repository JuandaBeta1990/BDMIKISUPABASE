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
    if not url:
        raise HTTPException(status_code=500, detail="DB1_URL no está configurado")
    try:
        return psycopg2.connect(url, cursor_factory=RealDictCursor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a BD1: {e}")

def get_db1():
    conn = _connect_postgres(DB1_URL)
    try:
        yield conn
    finally:
        conn.close()


# =====================================================
#   BASE DE DATOS 2 (SUPABASE – PROYECTO PRINCIPAL)
#   (mantengo exactamente como lo tienes)
# =====================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_APIKEY = os.getenv("SUPABASE_APIKEY")
SUPABASE_BEARER = os.getenv("SUPABASE_BEARER")

def supabase_get(table: str, params: dict = None):
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
    """Dependency: devuelve cliente Supabase (solo GET wrapper como ya estaba)."""
    def _client(table: str, params: dict = None):
        return supabase_get(table, params)
    return _client


# =====================================================
#   BASE DE DATOS 3 (SUPABASE – IMEXICO REAL ESTATE)
#   CLIENTE COMPLETO (GET / POST / PATCH / DELETE)
# =====================================================

SUPABASE2_URL = os.getenv("SUPABASE2_URL")
SUPABASE2_APIKEY = os.getenv("SUPABASE2_APIKEY")  # usar service_role/secret key como bearer

# Validación mínima de variables
if not SUPABASE2_URL or not SUPABASE2_APIKEY:
    print("Advertencia: Variables de Supabase2 no configuradas correctamente (SUPABASE2_URL / SUPABASE2_APIKEY)")

def _build_headers_for_supabase2():
    return {
        "apikey": SUPABASE2_APIKEY,
        "Authorization": f"Bearer {SUPABASE2_APIKEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def supabase2_get(table: str, params: dict = None):
    url = f"{SUPABASE2_URL}/rest/v1/{table}"
    headers = _build_headers_for_supabase2()
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Supabase2 GET: {e}")

def supabase2_post(table: str, data: dict):
    url = f"{SUPABASE2_URL}/rest/v1/{table}"
    headers = _build_headers_for_supabase2()
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Supabase2 POST: {e}")

def supabase2_patch(table: str, filters: dict, data: dict):
    url = f"{SUPABASE2_URL}/rest/v1/{table}"
    # convierte filtros {'id': 'uuid'} -> params {'id': 'eq.uuid'}
    params = {k: f"eq.{v}" for k, v in (filters or {}).items()}
    headers = _build_headers_for_supabase2()
    try:
        response = requests.patch(url, headers=headers, params=params, json=data)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Supabase2 PATCH: {e}")

def supabase2_delete(table: str, filters: dict):
    url = f"{SUPABASE2_URL}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in (filters or {}).items()}
    headers = _build_headers_for_supabase2()
    try:
        response = requests.delete(url, headers=headers, params=params)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        # Supabase puede devolver 204 o devolver representación dependiendo de Prefer
        if response.status_code in (200, 204):
            return {"deleted": True}
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Supabase2 DELETE: {e}")

def get_supabase2():
    """
    Devuelve un cliente con métodos:
      - select(table, params=None)  -> lista
      - insert(table, data)         -> creado
      - update(table, filters, data)-> actualizado
      - delete(table, filters)      -> borrado
    Uso: conn = Depends(get_supabase2); conn.select("units", {"project_id":"eq.<id>"})
    """
    class Supabase2Client:
        def select(self, table: str, params: dict = None):
            return supabase2_get(table, params)

        def insert(self, table: str, data: dict):
            return supabase2_post(table, data)

        def update(self, table: str, filters: dict, data: dict):
            return supabase2_patch(table, filters, data)

        def delete(self, table: str, filters: dict):
            return supabase2_delete(table, filters)

    return Supabase2Client()

# Alias estilo "BD3" para usar en Depends()
def get_db3():
    """Para endpoints que quieran la BD3 (Supabase IMEXICO) como cliente completo."""
    return get_supabase2()
