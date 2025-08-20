
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from database import get_connection
import random

def insert_sample_units():
    conn = get_connection()
    
    try:
        # Get existing projects
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM projects")
            projects = cur.fetchall()
            
        if not projects:
            print("No projects found. Please insert projects first.")
            return
            
        # Sample unit data
        typologies = ['Studio', '1BR', '2BR', '3BR', 'Penthouse']
        levels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'PH']
        statuses = ['Disponible', 'Reservada', 'Vendida', 'En construcción']
        
        units_to_insert = []
        
        for project in projects:
            # Create 5-15 units per project
            num_units = random.randint(5, 15)
            
            for i in range(1, num_units + 1):
                unit_id = str(uuid.uuid4())
                unit_identifier = f"{project['name'][:3].upper()}-{i:03d}"
                typology = random.choice(typologies)
                level = random.choice(levels)
                
                # Area based on typology
                area_ranges = {
                    'Studio': (35, 50),
                    '1BR': (55, 75),
                    '2BR': (75, 95),
                    '3BR': (95, 120),
                    'Penthouse': (150, 250)
                }
                area = round(random.uniform(*area_ranges[typology]), 2)
                
                status = random.choice(statuses)
                delivery_date = random.choice(['2024-Q4', '2025-Q1', '2025-Q2', '2025-Q3'])
                
                units_to_insert.append((
                    unit_id, str(project['id']), unit_identifier, typology, level,
                    area, status, delivery_date, None
                ))
        
        # Insert all units
        with conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO units (
                    id, project_id, unit_identifier, typology, level,
                    total_area_sqm, status, delivery_date, price_list_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, units_to_insert)
            
        conn.commit()
        print(f"Inserted {len(units_to_insert)} sample units successfully")
        
    except Exception as e:
        print(f"Error inserting sample units: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    insert_sample_units()
