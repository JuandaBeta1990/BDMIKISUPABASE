import uuid
from fastapi import HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
import schemas
import requests


# ============================================================
# =================== CRUD PARA ZONAS =========================
# ============================================================

def get_zone(conn, zone_id: int):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name, description FROM zones WHERE id = %s", (zone_id,))
        return cur.fetchone()

def get_zones(conn, skip: int = 0, limit: int = 100):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                z.id,
                z.name,
                z.description,
                COUNT(p.id) AS project_count
            FROM zones z
            LEFT JOIN projects p ON p.zone_id = z.id
            GROUP BY z.id, z.name, z.description
            ORDER BY z.id ASC
            LIMIT %s OFFSET %s
        """, (limit, skip))
        return cur.fetchall()

def update_zone(conn, zone_id: int, zone: schemas.ZoneUpdate):
    update_data = zone.model_dump(exclude_unset=True)
    if not update_data:
        return get_zone(conn, zone_id)

    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(zone_id)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"UPDATE zones SET {set_clause} WHERE id = %s", tuple(values))
        conn.commit()
    
    return get_zone(conn, zone_id)

def delete_zone(conn, zone_id: int):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM zones WHERE id = %s", (zone_id,))
        deleted = cur.rowcount
        conn.commit()
        return deleted

def create_zone(conn, zone: schemas.ZoneCreate):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO zones (name, description) VALUES (%s, %s) RETURNING id",
            (zone.name, zone.description)
        )
        new_id = cur.fetchone()["id"]
        conn.commit()
        return get_zone(conn, new_id)



# ============================================================
# ================= CRUD PARA PROYECTOS =======================
# ============================================================

def get_project(conn, project_id: uuid.UUID):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                p.id,
                p.name,
                p.zone_id,
                p.general_field_id,
                p.prices_field_id,
                z.name AS zone_name
            FROM projects p
            LEFT JOIN zones z ON p.zone_id = z.id
            WHERE p.id = %s
        """, (project_id,))
        return cur.fetchone()

def get_projects(conn, skip: int = 0, limit: int = 100, search: str = ""):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT 
                p.id,
                p.name,
                p.zone_id,
                p.general_field_id,
                p.prices_field_id,
                z.name AS zone_name
            FROM projects p
            LEFT JOIN zones z ON p.zone_id = z.id
        """

        params = []

        if search:
            query += " WHERE p.name ILIKE %s"
            params.append(f"%{search}%")

        query += " ORDER BY p.id ASC LIMIT %s OFFSET %s"
        params.extend([limit, skip])

        cur.execute(query, tuple(params))
        return cur.fetchall()

def create_project(conn, project: schemas.ProjectCreate):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            INSERT INTO projects (name, zone_id, general_field_id, prices_field_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        cur.execute(query, (
            project.name,
            project.zone_id,
            project.general_field_id,
            project.prices_field_id
        ))
        new_id = cur.fetchone()["id"]
        conn.commit()
        return get_project(conn, new_id)

def update_project(conn, project_id: uuid.UUID, project: schemas.ProjectUpdate):
    update_data = project.model_dump(exclude_unset=True)

    if not update_data:
        return get_project(conn, project_id)

    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(project_id)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"UPDATE projects SET {set_clause} WHERE id = %s",
            tuple(values)
        )
        conn.commit()

    return get_project(conn, project_id)

def delete_project(conn, project_id: uuid.UUID):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM projects WHERE id = %s", (str(project_id),))
        rowcount = cur.rowcount
        conn.commit()
        return rowcount



# ============================================================
# =================== CRUD DASHBOARD ==========================
# ============================================================

def get_dashboard_stats(conn):
    stats = {}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT COUNT(*) as total FROM projects")
        stats['total_projects'] = cur.fetchone()['total']
        cur.execute("SELECT COALESCE(SUM(total_units), 0) as total FROM projects")
        stats['total_units'] = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as total FROM zones")
        stats['total_zones'] = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as total FROM units WHERE status ILIKE 'Disponible'")
        stats['available_units'] = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as total FROM units WHERE status ILIKE 'Vendida'")
        stats['sold_units'] = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as total FROM units WHERE status ILIKE 'Reservada'")
        stats['reserved_units'] = cur.fetchone()['total']
        cur.execute("SELECT COUNT(DISTINCT developer) as total FROM projects WHERE developer IS NOT NULL")
        stats['total_developers'] = cur.fetchone()['total']
    return stats

def get_recent_activity(conn, limit: int = 10):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                'project' as type,
                p.name as title,
                'Proyecto creado' as action,
                p.created_at as timestamp,
                p.developer as description
            FROM projects p
            UNION ALL
            SELECT 
                'unit' as type,
                CONCAT(pr.name, ' - ', u.unit_identifier) as title,
                CASE 
                    WHEN u.status = 'Vendida' THEN 'Unidad vendida'
                    WHEN u.status = 'Reservada' THEN 'Unidad reservada'
                    ELSE 'Unidad actualizada'
                END as action,
                u.updated_at as timestamp,
                u.status as description
            FROM units u
            JOIN projects pr ON u.project_id = pr.id
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()

def get_projects_by_zone(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                COALESCE(z.name, 'Sin zona') as zone_name,
                COUNT(p.id) as project_count
            FROM projects p
            LEFT JOIN zones z ON p.zone = z.id
            GROUP BY z.name
            ORDER BY project_count DESC
        """)
        return cur.fetchall()

def get_units_by_status(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                COALESCE(status, 'Sin estado') as status,
                COUNT(*) as unit_count
            FROM units
            GROUP BY status
            ORDER BY unit_count DESC
        """)
        return cur.fetchall()



# ============================================================
# ==================== CRUD USUARIOS ==========================
# ============================================================

def get_user(conn, user_id: int):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, username, role, password_hash FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()

def get_users(conn, skip: int = 0, limit: int = 100, role_filter: str = ""):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = "SELECT * FROM users"
        params = []

        if role_filter:
            query += " WHERE role = %s"
            params.append(role_filter)

        query += " ORDER BY id DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])

        cur.execute(query, tuple(params))
        return cur.fetchall()

def create_user(conn, user: schemas.UserCreate):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO users (username, role, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """,
        (user.username, user.role, user.password))
        
        new_id = cur.fetchone()["id"]
        conn.commit()
        return get_user(conn, new_id)

def update_user(conn, user_id: int, user: schemas.UserUpdate):
    update_data = user.model_dump(exclude_unset=True)

    if not update_data:
        return get_user(conn, user_id)

    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(user_id)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"UPDATE users SET {set_clause} WHERE id = %s",
            tuple(values)
        )
        conn.commit()

    return get_user(conn, user_id)

def delete_user(conn, user_id: int):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        deleted = cur.rowcount
        conn.commit()
        return deleted



# ============================================================
# =================== CRUD UNIDADES (SUPABASE2) ===============
# ============================================================

def _validate_uuid_str(id_str: str):
    try:
        return str(uuid.UUID(str(id_str)))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid UUID")


def get_unit(conn, unit_id: str):
    unit_id = _validate_uuid_str(unit_id)
    rows = conn.select("units", {"id": f"eq.{unit_id}"})
    return rows[0] if rows else None


def get_all_units(conn, skip: int = 0, limit: int = 1000):
    rows = conn.select("units")
    return rows[skip: skip + limit]


def get_units_by_project(conn, project_id: str):
    project_id = _validate_uuid_str(project_id)
    rows = conn.select("units", {"project_id": f"eq.{project_id}"})
    return rows


def create_unit(conn, unit: schemas.UnitCreate):
    payload = unit.model_dump() if hasattr(unit, "model_dump") else unit.dict()
    created = conn.insert("units", payload)
    return created[0] if isinstance(created, list) and created else created


def update_unit(conn, unit_id: str, unit: schemas.UnitUpdate):
    unit_id = _validate_uuid_str(unit_id)
    payload = unit.model_dump(exclude_unset=True)
    if not payload:
        return get_unit(conn, unit_id)

    updated = conn.update("units", {"id": unit_id}, payload)
    return updated[0] if isinstance(updated, list) and updated else updated


def delete_unit(conn, unit_id: str):
    unit_id = _validate_uuid_str(unit_id)
    res = conn.delete("units", {"id": unit_id})
    return res



# ============================================================
# ================ UTILIDAD EXTRA - PROYECTOS =================
# ============================================================

def get_all_projects(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, zone, general_field_id, prices_field_id
            FROM projects
            ORDER BY id ASC
        """)
        return cur.fetchall()
