"""Check PostgreSQL/PostGIS availability without changing the machine."""
import os
import sys

try:
    import psycopg2
except ImportError:
    print('psycopg2 is not installed in the active Python environment.')
    sys.exit(2)

host = os.getenv('POSTGRES_HOST', 'localhost')
port = os.getenv('POSTGRES_PORT', '5432')
database = os.getenv('POSTGRES_DB', 'ndvi_ai')
user = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
try:
    with psycopg2.connect(host=host, port=port, database=database, user=user, password=password, connect_timeout=3) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT PostGIS_Full_Version()")
            print(f'PostGIS available: {cur.fetchone()[0]}')
except Exception as exc:
    print(f'PostGIS unavailable at {host}:{port}/{database}: {exc}')
    sys.exit(1)
