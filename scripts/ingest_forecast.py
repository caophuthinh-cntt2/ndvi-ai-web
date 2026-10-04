#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Forecast Data
Extracts forecast ZIP, reads CSV and GeoJSON, inserts forecast results and study area boundary
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import zipfile
import shutil

import pandas as pd
import geopandas as gpd
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent / 'data' / 'logs' / f'ingest_forecast_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SOURCE_DATA_DIR = Path(os.getenv('SOURCE_DATA_DIR', 'D:/NDVI'))
PROCESSED_DATA_DIR = Path(os.getenv('PROCESSED_DATA_DIR', 'D:/NDVI/ndvi-ai-web/data/processed'))
CACHE_DIR = Path(os.getenv('CACHE_DIR', 'D:/NDVI/ndvi-ai-web/data/cache'))

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'ndvi_ai'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )

def extract_forecast_zip(zip_path: Path, extract_dir: Path) -> Path:
    """Extract forecast ZIP file"""
    
    logger.info(f"Extracting {zip_path.name}...")
    
    if extract_dir.exists():
        logger.info(f"Extract directory already exists: {extract_dir}")
        return extract_dir
    
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    files = list(extract_dir.glob('*'))
    logger.info(f"✓ Extracted {len(files)} files")
    
    return extract_dir

def ingest_forecast_csv(csv_path: Path, model_run_id: int, conn) -> int:
    """
    Read forecast CSV and insert to database
    
    CSV format expected:
    Month,NDVI_Forecast
    2026-01,0.5347
    2026-02,0.5247
    ...
    """
    
    logger.info(f"Reading forecast CSV: {csv_path.name}")
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return 0
    
    # Read CSV
    df = pd.read_csv(csv_path)
    logger.info(f"  Loaded {len(df)} forecast records")
    
    # Expected columns
    if 'Month' not in df.columns or 'NDVI_Forecast' not in df.columns:
        logger.warning(f"CSV columns: {df.columns.tolist()}")
        # Try to infer from first two columns
        df.columns = ['Month', 'NDVI_Forecast']
    
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        month_str = str(row['Month'])
        ndvi_value = float(row['NDVI_Forecast'])
        
        # Parse date (format: 2026-01 or 2026-01-01)
        if len(month_str) == 7:  # YYYY-MM
            forecast_date = f"{month_str}-01"
        else:
            forecast_date = month_str
        
        year = int(month_str[:4])
        month = int(month_str[5:7])
        
        # Check if exists
        cursor.execute("""
            SELECT id FROM forecast_results 
            WHERE model_run_id = %s AND forecast_date = %s
        """, (model_run_id, forecast_date))
        
        if cursor.fetchone():
            logger.debug(f"  Forecast for {forecast_date} already exists, skipping")
            continue
        
        # Insert forecast
        cursor.execute("""
            INSERT INTO forecast_results (
                model_run_id, forecast_date, year, month, 
                predicted_ndvi, is_extrapolation
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (model_run_id, forecast_date, year, month, ndvi_value, True))
        
        inserted += 1
    
    conn.commit()
    logger.info(f"✓ Inserted {inserted} forecast records")
    
    return inserted

def ingest_geojson_boundary(geojson_path: Path, conn) -> int:
    """Read GeoJSON and insert study area boundary"""
    
    logger.info(f"Reading GeoJSON: {geojson_path.name}")
    
    if not geojson_path.exists():
        logger.warning(f"GeoJSON file not found: {geojson_path}")
        return 0
    
    # Read GeoJSON
    gdf = gpd.read_file(geojson_path)
    logger.info(f"  Loaded {len(gdf)} features")
    
    if len(gdf) == 0:
        logger.warning("No features in GeoJSON")
        return 0
    
    cursor = conn.cursor()
    
    # Check if study area already exists
    cursor.execute("SELECT id FROM study_areas WHERE name = %s", ('Ho Chi Minh City',))
    existing = cursor.fetchone()
    
    if existing:
        logger.info(f"✓ Study area already exists (ID: {existing[0]})")
        return existing[0]
    
    # Get first geometry
    geom = gdf.geometry.iloc[0]
    geom_wkt = geom.wkt
    
    # Insert study area
    cursor.execute("""
        INSERT INTO study_areas (name, description, geom)
        VALUES (%s, %s, ST_GeomFromText(%s, 4326))
        RETURNING id
    """, (
        'Ho Chi Minh City',
        'Ho Chi Minh City boundary from forecast GeoJSON',
        geom_wkt
    ))
    
    study_area_id = cursor.fetchone()[0]
    conn.commit()
    
    logger.info(f"✓ Study area inserted (ID: {study_area_id})")
    
    return study_area_id

def copy_forecast_maps(extract_dir: Path, output_dir: Path):
    """Copy forecast PNG maps to processed directory"""
    
    logger.info("Copying forecast maps...")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    png_files = list(extract_dir.glob('*.png'))
    
    if len(png_files) == 0:
        logger.warning("No PNG files found in extract directory")
        return
    
    copied = 0
    for png_file in png_files:
        dest = output_dir / png_file.name
        if not dest.exists():
            shutil.copy2(png_file, dest)
            copied += 1
    
    logger.info(f"✓ Copied {copied} forecast maps to {output_dir}")

def main():
    """Main forecast ingestion process"""
    
    print("="*60)
    print("NDVI Forecast Data Ingestion")
    print("="*60)
    
    # Locate ZIP file
    zip_path = SOURCE_DATA_DIR / 'HCM_NDVI_Forecast_Maps_2026.zip'
    
    if not zip_path.exists():
        logger.error(f"✗ Forecast ZIP not found: {zip_path}")
        sys.exit(1)
    
    try:
        conn = get_db_connection()
        logger.info("✓ Connected to database")
        
        # Extract ZIP
        extract_dir = CACHE_DIR / 'forecast_extract'
        extract_forecast_zip(zip_path, extract_dir)
        
        # Find model run (Random Forest - the selected model)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM model_runs 
            WHERE model_type = 'RANDOM_FOREST' AND is_selected = TRUE
            ORDER BY created_at DESC LIMIT 1
        """)
        
        model_run = cursor.fetchone()
        
        if not model_run:
            logger.warning("No Random Forest model found. Creating placeholder...")
            # Will be created by ingest_model_metrics.py
            logger.info("Please run ingest_model_metrics.py first")
            conn.close()
            return
        
        model_run_id = model_run[0]
        logger.info(f"✓ Using model run ID: {model_run_id}")
        
        # Ingest forecast CSV
        csv_path = extract_dir / 'HCM_NDVI_Forecast_2026.csv'
        ingest_forecast_csv(csv_path, model_run_id, conn)
        
        # Ingest GeoJSON boundary
        geojson_path = extract_dir / 'HCM_NDVI_Forecast_2026.geojson'
        ingest_geojson_boundary(geojson_path, conn)
        
        # Copy PNG maps
        maps_output_dir = PROCESSED_DATA_DIR / 'forecast_maps'
        copy_forecast_maps(extract_dir, maps_output_dir)
        
        conn.close()
        
        print("\n" + "="*60)
        print("✓ Forecast ingestion completed successfully!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
