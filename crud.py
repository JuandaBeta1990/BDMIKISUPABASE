import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
import schemas # <-- CORRECCIÓN: Se cambió de 'from . import schemas' a una importación directa.

# --- CRUD para Zonas ---
def get_zone(conn, zone_id: uuid.UUID):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM zones WHERE id = %s", (str(zone_id),))
        return cur.fetchone()

def get_zones(conn, skip: int = 0, limit: int = 100):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT z.*, COUNT(p.id) AS project_count
            FROM zones z LEFT JOIN projects p ON z.id = p.zone
            GROUP BY z.id ORDER BY z.name LIMIT %s OFFSET %s
        """, (limit, skip))
        return cur.fetchall()

def create_zone(conn, zone: schemas.ZoneCreate):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("INSERT INTO zones (name, description) VALUES (%s, %s) RETURNING *", (zone.name, zone.description))
        new_zone = cur.fetchone()
        conn.commit()
        return new_zone

# --- CRUD para Proyectos ---
def get_project(conn, project_id: uuid.UUID):
    """Obtiene un único proyecto por su ID, incluyendo el nombre de la zona."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT p.*, z.name as zone_name FROM projects p LEFT JOIN zones z ON p.zone = z.id WHERE p.id = %s", (str(project_id),))
        return cur.fetchone()

def get_projects(conn, skip: int = 0, limit: int = 100, search: str = ""):
    """Obtiene una lista de proyectos, con paginación y búsqueda."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT p.id, p.name, p.slug, p.developer, p.total_units, p.accepts_crypto,
                   z.name as zone_name 
            FROM projects p
            LEFT JOIN zones z ON p.zone = z.id
        """
        params = []
        if search:
            query += " WHERE p.name ILIKE %s OR p.developer ILIKE %s"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])

        cur.execute(query, tuple(params))
        return cur.fetchall()

def create_project(conn, project: schemas.ProjectCreate):
    """Crea un nuevo proyecto en la base de datos."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        new_id = str(uuid.uuid4())
        query = """
            INSERT INTO projects (
                id, name, slug, zone, sub_zone, developer, maps_url, concept, total_units,
                delivery_summary, brochure_slug, render_slug, tour_url, admin_type,
                accepts_crypto, turn_key, has_ocean_view, condo_regime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            new_id, project.name, project.slug, project.zone, project.sub_zone, project.developer,
            project.maps_url, project.concept, project.total_units, project.delivery_summary,
            project.brochure_slug, project.render_slug, project.tour_url, project.admin_type,
            project.accepts_crypto, project.turn_key, project.has_ocean_view, project.condo_regime
        )
        cur.execute(query, params)
        new_project_id = cur.fetchone()['id']
        conn.commit()
        return get_project(conn, new_project_id)

def update_project(conn, project_id: uuid.UUID, project: schemas.ProjectUpdate):
    """Actualiza un proyecto existente."""
    update_data = project.model_dump(exclude_unset=True)
    if not update_data:
        return get_project(conn, project_id)

    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(str(project_id))

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = f"UPDATE projects SET {set_clause}, updated_at = NOW() WHERE id = %s"
        cur.execute(query, tuple(values))
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
    return stats

# --- CRUD para Unidades ---
def get_unit(conn, unit_id: uuid.UUID):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM units WHERE id = %s", (str(unit_id),))
        return cur.fetchone()

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
