import os
import urllib.request
from sqlalchemy import create_engine, inspect

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ecommerce")
CHINOOK_URL = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_PostgreSql.sql"

def check_data_exists(engine) -> bool:
    """Checks if the core Chinook tables already exist in the database."""
    inspector = inspect(engine)
    # Convert all returned table names to lowercase to prevent casing mismatches
    existing_tables = [table.lower() for table in inspector.get_table_names()]
    # Chinook uses exact casing for tables
    return "album" in existing_tables and "artist" in existing_tables

def ingest_chinook():
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    
    # --- SAFETY CHECK ---
    if check_data_exists(engine):
        print("✅ Chinook data already exists in the database. Skipping download and ingestion.")
        return
    # --------------------

    print(f"Downloading Chinook SQL script from {CHINOOK_URL}...")
    
    req = urllib.request.Request(CHINOOK_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        sql_script = response.read().decode('utf-8')
        
    cleaned_lines = []
    for line in sql_script.splitlines():
        upper_line = line.strip().upper()
        if upper_line.startswith('\\') or upper_line.startswith('DROP DATABASE') or upper_line.startswith('CREATE DATABASE'):
            continue
        cleaned_lines.append(line)
        
    clean_sql_script = "\n".join(cleaned_lines)
    print("Download complete. Connecting to PostgreSQL container...")
    
    print("Ingesting tables and data. This may take 5-10 seconds...")
    
    conn = engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(clean_sql_script)
        cursor.close()
        print("✅ Chinook database successfully ingested!")
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ingest_chinook()