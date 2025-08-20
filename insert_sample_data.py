
import psycopg2
import os
from uuid import uuid4

# Database configuration
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mikiai")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "password")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")

def get_connection():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    else:
        conn_string = f"host='{DATABASE_HOST}' dbname='{DATABASE_NAME}' user='{DATABASE_USER}' password='{DATABASE_PASSWORD}' port='{DATABASE_PORT}'"
        return psycopg2.connect(conn_string)

def insert_sample_data():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Insertar zonas de ejemplo
        zone_ids = []
        zones = [
            ("Zona Norte", "Zona turística principal"),
            ("Centro", "Centro histórico y comercial"),
            ("Playa", "Zona costera y hoteles")
        ]
        
        for name, description in zones:
            zone_id = str(uuid4())
            zone_ids.append(zone_id)
            cur.execute(
                "INSERT INTO zones (id, name, description) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (zone_id, name, description)
            )
        
        # Insertar proyectos de ejemplo
        projects = [
            {
                "name": "Residencial Marina Bay",
                "slug": "marina-bay",
                "zone": zone_ids[0],
                "developer": "Desarrollos del Caribe",
                "total_units": 120,
                "concept": "Apartamentos frente al mar",
                "accepts_crypto": True,
                "turn_key": True,
                "has_ocean_view": True
            },
            {
                "name": "Torres del Centro",
                "slug": "torres-centro",
                "zone": zone_ids[1],
                "developer": "Constructora Moderna",
                "total_units": 80,
                "concept": "Apartamentos en el centro de la ciudad",
                "accepts_crypto": False,
                "turn_key": False,
                "has_ocean_view": False
            },
            {
                "name": "Villas Playa Dorada",
                "slug": "villas-playa",
                "zone": zone_ids[2],
                "developer": "Inmobiliaria Premium",
                "total_units": 45,
                "concept": "Villas de lujo en primera línea de playa",
                "accepts_crypto": True,
                "turn_key": True,
                "has_ocean_view": True
            }
        ]
        
        for project in projects:
            project_id = str(uuid4())
            cur.execute("""
                INSERT INTO projects (
                    id, name, slug, zone, developer, total_units, concept,
                    accepts_crypto, turn_key, has_ocean_view, condo_regime
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                project_id, project["name"], project["slug"], project["zone"],
                project["developer"], project["total_units"], project["concept"],
                project["accepts_crypto"], project["turn_key"], project["has_ocean_view"], False
            ))
        
        conn.commit()
        print("Datos de ejemplo insertados correctamente")
        
    except Exception as e:
        print(f"Error al insertar datos: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    insert_sample_data()
