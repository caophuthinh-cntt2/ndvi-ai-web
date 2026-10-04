#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Database Script
Creates PostgreSQL database, enables PostGIS, and runs schema.sql
"""
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Setup database with PostGIS extension and schema"""
    
    # Database configuration
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    db_name = os.getenv('POSTGRES_DB', 'ndvi_ai')
    
    print("="*60)
    print("NDVI AI WebGIS - Database Setup")
    print("="*60)
    
    try:
        # Step 1: Connect to default postgres database
        print(f"\n[1/4] Connecting to PostgreSQL at {db_host}:{db_port}...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database='postgres',
            user=db_user,
            password=db_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Step 2: Create database if not exists
        print(f"[2/4] Checking database '{db_name}'...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        
        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE {db_name}')
            print(f"✓ Database '{db_name}' created successfully")
        else:
            print(f"✓ Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        
        # Step 3: Connect to target database and enable PostGIS
        print(f"[3/4] Enabling PostGIS extension...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        conn.commit()
        print("✓ PostGIS extension enabled")
        
        # Step 4: Execute schema
        print(f"[4/4] Creating database schema...")
        schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
        
        if not schema_path.exists():
            print(f"✗ Schema file not found: {schema_path}")
            sys.exit(1)
        
        with open(schema_path, 'r', encoding='utf-8-sig') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        print("✓ Database schema created successfully")
        
        # Verify tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✓ Database setup completed successfully!")
        print("="*60)
        print(f"\nConnection string: postgresql://{db_user}@{db_host}:{db_port}/{db_name}")
        
    except psycopg2.Error as e:
        print(f"\n✗ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    setup_database()
