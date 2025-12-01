import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
import schemas # <-- CORRECCIÓN: Se cambió de 'from . import schemas' a una importación directa.

# --- CRUD para Zonas ---
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


# --- CRUD para Proyectos ---
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
    """Elimina un proyecto por su ID."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM projects WHERE id = %s", (str(project_id),))
        rowcount = cur.rowcount
        conn.commit()
        return rowcount

# --- CRUD para Dashboard ---
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

# --- CRUD para Usuarios ---
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

        query += " ORDER BY id DESC"
        query += " LIMIT %s OFFSET %s"

        params.extend([limit, skip])

        cur.execute(query, tuple(params))
        return cur.fetchall()

def create_user(conn, user: schemas.UserCreate):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO users (username, role, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user.username, user.role, user.password)
        )
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

# --- CRUD para Unidades ---
def get_unit(conn, unit_id: uuid.UUID):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM units WHERE id = %s", (str(unit_id),))
        return cur.fetchone()

def get_all_units(conn, skip: int = 0, limit: int = 1000):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT u.*, p.name as project_name 
            FROM units u 
            LEFT JOIN projects p ON u.project_id = p.id 
            ORDER BY p.name, u.unit_identifier 
            LIMIT %s OFFSET %s
        """, (limit, skip))
        return cur.fetchall()

def get_units_by_project(conn, project_id: uuid.UUID):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM units WHERE project_id = %s ORDER BY unit_identifier", (str(project_id),))
        return cur.fetchall()

def create_unit(conn, unit: schemas.UnitCreate):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO units (
                project_id, unit_identifier, typology, level, 
                total_area_sqm, status, delivery_date, price_list_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                unit.project_id, unit.unit_identifier, unit.typology, unit.level,
                unit.total_area_sqm, unit.status, unit.delivery_date, unit.price_list_url
            )
        )
        new_unit = cur.fetchone()
        conn.commit()
        return new_unit

def update_unit(conn, unit_id: uuid.UUID, unit: schemas.UnitUpdate):
    update_data = unit.model_dump(exclude_unset=True)
    if not update_data:
        return get_unit(conn, unit_id)

    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(str(unit_id))

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = f"UPDATE units SET {set_clause}, updated_at = NOW() WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()
    return get_unit(conn, unit_id)

def delete_unit(conn, unit_id: uuid.UUID):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("DELETE FROM units WHERE id = %s RETURNING *", (str(unit_id),))
        deleted_unit = cur.fetchone()
        conn.commit()
        return deleted_unit

def get_all_projects(conn):
    """Obtiene todos los proyectos con sus columnas principales."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, zone, general_field_id, prices_field_id
            FROM projects
            ORDER BY id ASC
        """)
        return cur.fetchall()
