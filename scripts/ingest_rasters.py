#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Raster Datasets
Scans for GeoTIFF files, converts to COG, computes statistics, and registers in database
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import json

import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import box
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent))
from convert_to_cog import convert_to_cog

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent / 'data' / 'logs' / f'ingest_rasters_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SOURCE_DATA_DIR = Path(os.getenv('SOURCE_DATA_DIR', 'D:/NDVI'))
PROCESSED_DATA_DIR = Path(os.getenv('PROCESSED_DATA_DIR', 'D:/NDVI/ndvi-ai-web/data/processed'))
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'ndvi_ai'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )

def compute_raster_statistics(raster_path: Path) -> dict:
    """
    Compute comprehensive statistics from raster
    
    Returns:
        dict: Statistics including min, max, mean, median, std, counts, histogram
    """
    logger.info(f"Computing statistics for {raster_path.name}...")
    
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        
        # Handle nodata
        if src.nodata is not None:
            mask = data != src.nodata
        else:
            mask = np.ones_like(data, dtype=bool)
        
        valid_data = data[mask]
        
        if len(valid_data) == 0:
            logger.warning("No valid pixels found!")
            return None
        
        # Basic statistics
        stats = {
            'min_value': float(np.min(valid_data)),
            'max_value': float(np.max(valid_data)),
            'mean_value': float(np.mean(valid_data)),
            'median_value': float(np.median(valid_data)),
            'std_dev': float(np.std(valid_data)),
            'valid_pixel_count': int(np.sum(mask)),
            'total_pixel_count': int(data.size)
        }
        
        # NDVI class counts
        stats['ndvi_negative_count'] = int(np.sum(valid_data < 0))
        stats['ndvi_bare_soil_count'] = int(np.sum((valid_data >= 0) & (valid_data < 0.2)))
        stats['ndvi_low_vegetation_count'] = int(np.sum((valid_data >= 0.2) & (valid_data < 0.4)))
        stats['ndvi_moderate_vegetation_count'] = int(np.sum((valid_data >= 0.4) & (valid_data < 0.6)))
        stats['ndvi_high_vegetation_count'] = int(np.sum(valid_data >= 0.6))
        
        # Histogram
        hist, bin_edges = np.histogram(valid_data, bins=50)
        stats['histogram_json'] = {
            'counts': hist.tolist(),
            'bin_edges': bin_edges.tolist()
        }
        
        logger.info(f"  Min: {stats['min_value']:.4f}, Max: {stats['max_value']:.4f}")
        logger.info(f"  Mean: {stats['mean_value']:.4f}, Median: {stats['median_value']:.4f}")
        logger.info(f"  Valid pixels: {stats['valid_pixel_count']:,} / {stats['total_pixel_count']:,}")
        
        return stats

def ingest_raster(
    input_path: Path,
    name: str,
    dataset_type: str,
    year: int,
    observation_date: str = None,
    conn = None
) -> int:
    """
    Ingest a single raster dataset (idempotent)
    
    Returns:
        int: Dataset ID
    """
    logger.info("="*60)
    logger.info(f"Ingesting: {name}")
    logger.info("="*60)
    
    cursor = conn.cursor()
    
    # Check if already exists
    cursor.execute("SELECT id FROM raster_datasets WHERE name = %s", (name,))
    existing = cursor.fetchone()
    
    if existing:
        logger.info(f"✓ Dataset '{name}' already exists (ID: {existing[0]}). Skipping.")
        return existing[0]
    
    # Read raster metadata
    logger.info(f"Reading metadata from {input_path.name}...")
    with rasterio.open(input_path) as src:
        crs = src.crs.to_string() if src.crs else 'EPSG:4326'
        width = src.width
        height = src.height
        bounds_tuple = src.bounds
        resolution_x = src.res[0]
        resolution_y = src.res[1]
        nodata = src.nodata
        dtype = str(src.dtypes[0])
        
        # Create bounds geometry
        bounds_wkt = f"POLYGON(({bounds_tuple.left} {bounds_tuple.bottom}, {bounds_tuple.right} {bounds_tuple.bottom}, {bounds_tuple.right} {bounds_tuple.top}, {bounds_tuple.left} {bounds_tuple.top}, {bounds_tuple.left} {bounds_tuple.bottom}))"
        
        metadata = {
            'transform': list(src.transform),
            'count': src.count,
            'bounds': [bounds_tuple.left, bounds_tuple.bottom, bounds_tuple.right, bounds_tuple.top]
        }
    
    logger.info(f"  CRS: {crs}")
    logger.info(f"  Dimensions: {width} x {height}")
    logger.info(f"  Resolution: {resolution_x:.6f} x {resolution_y:.6f}")
    
    # Convert to COG
    cog_output = PROCESSED_DATA_DIR / f"{name}_cog.tif"
    logger.info(f"Converting to COG...")
    
    try:
        cog_path = convert_to_cog(str(input_path), str(cog_output))
    except Exception as e:
        logger.error(f"COG conversion failed: {e}")
        raise
    
    # Compute statistics
    stats = compute_raster_statistics(cog_output)
    
    if stats is None:
        logger.error("Failed to compute statistics. Aborting.")
        return None
    
    # Insert dataset
    logger.info("Inserting into database...")
    
    obs_date = observation_date if observation_date else f"{year}-12-31"
    
    cursor.execute("""
        INSERT INTO raster_datasets (
            name, dataset_type, observation_date, year,
            file_path, cog_path, crs, width, height,
            resolution_x, resolution_y, bounds, nodata_value, dtype, metadata_json
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326), %s, %s, %s
        ) RETURNING id
    """, (
        name, dataset_type, obs_date, year,
        str(input_path), str(cog_path), crs, width, height,
        resolution_x, resolution_y, bounds_wkt, nodata, dtype, Json(metadata)
    ))
    
    dataset_id = cursor.fetchone()[0]
    logger.info(f"✓ Dataset registered (ID: {dataset_id})")
    
    # Insert statistics
    cursor.execute("""
        INSERT INTO raster_statistics (
            dataset_id, min_value, max_value, mean_value, median_value, std_dev,
            valid_pixel_count, total_pixel_count,
            ndvi_negative_count, ndvi_bare_soil_count, ndvi_low_vegetation_count,
            ndvi_moderate_vegetation_count, ndvi_high_vegetation_count, histogram_json
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """, (
        dataset_id, stats['min_value'], stats['max_value'], stats['mean_value'],
        stats['median_value'], stats['std_dev'], stats['valid_pixel_count'],
        stats['total_pixel_count'], stats['ndvi_negative_count'], stats['ndvi_bare_soil_count'],
        stats['ndvi_low_vegetation_count'], stats['ndvi_moderate_vegetation_count'],
        stats['ndvi_high_vegetation_count'], Json(stats['histogram_json'])
    ))
    
    conn.commit()
    logger.info(f"✓ Statistics saved")
    
    return dataset_id

def main():
    """Main ingestion process"""
    
    print("="*60)
    print("NDVI Raster Ingestion Pipeline")
    print("="*60)
    
    # Define datasets to ingest
    datasets = [
        {
            'file': 'HCM_NDVI_2015.tif',
            'name': 'HCM_NDVI_2015',
            'dataset_type': 'NDVI_OBSERVED',
            'year': 2015,
            'observation_date': '2015-12-31'
        },
        {
            'file': 'HCM_NDVI_2025.tif',
            'name': 'HCM_NDVI_2025',
            'dataset_type': 'NDVI_OBSERVED',
            'year': 2025,
            'observation_date': '2025-12-31'
        },
        {
            'file': 'HCM_NDVI_Change_2015_2025.tif',
            'name': 'HCM_NDVI_Change_2015_2025',
            'dataset_type': 'NDVI_CHANGE',
            'year': 2025,
            'observation_date': '2025-12-31'
        }
    ]
    
    try:
        conn = get_db_connection()
        logger.info(f"✓ Connected to database")
        
        results = []
        
        for ds in datasets:
            input_path = SOURCE_DATA_DIR / ds['file']
            
            if not input_path.exists():
                logger.warning(f"⚠ File not found: {input_path}")
                continue
            
            try:
                dataset_id = ingest_raster(
                    input_path=input_path,
                    name=ds['name'],
                    dataset_type=ds['dataset_type'],
                    year=ds['year'],
                    observation_date=ds['observation_date'],
                    conn=conn
                )
                results.append({'name': ds['name'], 'id': dataset_id, 'status': 'success'})
            except Exception as e:
                logger.error(f"✗ Failed to ingest {ds['name']}: {e}")
                results.append({'name': ds['name'], 'id': None, 'status': 'failed', 'error': str(e)})
                conn.rollback()
        
        conn.close()
        
        # Summary
        print("\n" + "="*60)
        print("Ingestion Summary")
        print("="*60)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"✓ Successfully ingested: {success_count}/{len(datasets)}")
        
        for r in results:
            status_icon = "✓" if r['status'] == 'success' else "✗"
            print(f"  {status_icon} {r['name']}: {r['status']}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
