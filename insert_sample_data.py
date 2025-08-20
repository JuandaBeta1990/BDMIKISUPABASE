
import psycopg2
from uuid import uuid4
from database import get_connection

def insert_sample_data():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Insertar zonas de ejemplo
        zone_ids = []
        zones = [
            ("Tulum", "Zona turística con cenotes y ruinas mayas"),
            ("Playa del Carmen", "Centro turístico de la Riviera Maya"),
            ("Cozumel", "Isla turística con arrecifes de coral"),
            ("Cancún", "Destino turístico internacional"),
            ("Puerto Morelos", "Pueblo mágico pesquero")
        ]
        
        for name, description in zones:
            zone_id = str(uuid4())
            zone_ids.append(zone_id)
            cur.execute(
                "INSERT INTO zones (id, name, description) VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING",
                (zone_id, name, description)
            )
        
        # Insertar proyectos de ejemplo
        projects = [
            {
                "name": "Residencial Marina Bay",
                "slug": "marina-bay",
                "zone": zone_ids[0],  # Tulum
                "developer": "Desarrollos del Caribe",
                "total_units": 120,
                "concept": "Apartamentos frente al mar con vista a cenotes",
                "accepts_crypto": True,
                "turn_key": True,
                "has_ocean_view": True,
                "condo_regime": True
            },
            {
                "name": "Torres del Centro",
                "slug": "torres-centro",
                "zone": zone_ids[1],  # Playa del Carmen
                "developer": "Constructora Moderna",
                "total_units": 80,
                "concept": "Apartamentos en el centro de la ciudad",
                "accepts_crypto": False,
                "turn_key": False,
                "has_ocean_view": False,
                "condo_regime": True
            },
            {
                "name": "Cozumel Paradise",
                "slug": "cozumel-paradise",
                "zone": zone_ids[2],  # Cozumel
                "developer": "Island Developers",
                "total_units": 60,
                "concept": "Condominios de lujo en isla tropical",
                "accepts_crypto": True,
                "turn_key": True,
                "has_ocean_view": True,
                "condo_regime": True
            }
        ]
        
        for project in projects:
            project_id = str(uuid4())
            cur.execute("""
                INSERT INTO projects (
                    id, name, slug, zone, developer, total_units, concept,
                    accepts_crypto, turn_key, has_ocean_view, condo_regime
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (slug) DO NOTHING
            """, (
                project_id, project["name"], project["slug"], project["zone"], 
                project["developer"], project["total_units"], project["concept"],
                project["accepts_crypto"], project["turn_key"], 
                project["has_ocean_view"], project["condo_regime"]
            ))
        
        conn.commit()
        print("Datos de ejemplo insertados correctamente")
        
    except Exception as e:
        print(f"Error insertando datos de ejemplo: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    insert_sample_data()
