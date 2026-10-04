#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Ingestion Script
Runs all data ingestion steps in the correct order
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import subprocess

# Setup logging
log_file = Path(__file__).parent.parent / 'data' / 'logs' / f'ingest_all_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_name: str, description: str) -> bool:
    """
    Run a Python script and return success status
    
    Args:
        script_name: Name of the script file
        description: Human-readable description
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    logger.info("="*70)
    logger.info(f"STEP: {description}")
    logger.info("="*70)
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        logger.error(f"✗ Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        logger.info(f"✓ {description} completed successfully\n")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed!")
        logger.error(f"Error output:\n{e.stderr}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error running {script_name}: {e}")
        return False

def main():
    """Main orchestration function"""
    
    start_time = datetime.now()
    
    print("\n")
    print("="*70)
    print(" "*20 + "NDVI AI WebGIS")
    print(" "*15 + "Complete Data Ingestion Pipeline")
    print("="*70)
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log file: {log_file}")
    print("="*70)
    print("\n")
    
    # Define ingestion steps
    steps = [
        ('setup_database.py', 'Database Setup & Schema Creation'),
        ('ingest_model_metrics.py', 'Model Metrics Ingestion'),
        ('ingest_rasters.py', 'Raster Datasets Ingestion'),
        ('ingest_forecast.py', 'Forecast Data Ingestion'),
        ('ingest_timeseries.py', 'Time Series Ingestion'),
    ]
    
    results = []
    
    # Execute each step
    for i, (script, description) in enumerate(steps, 1):
        print(f"\n[{i}/{len(steps)}] Running: {description}...")
        success = run_script(script, description)
        results.append({
            'step': description,
            'script': script,
            'success': success
        })
        
        if not success:
            logger.warning(f"⚠ Step failed but continuing with next steps...")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n\n")
    print("="*70)
    print(" "*25 + "INGESTION SUMMARY")
    print("="*70)
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    for i, result in enumerate(results, 1):
        status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
        print(f"{i}. {result['step']:<45} {status}")
    
    print("="*70)
    print(f"Completed: {success_count}/{total_count} steps successful")
    print(f"Duration: {duration.total_seconds():.1f} seconds")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    if success_count == total_count:
        print("\n✓ All ingestion steps completed successfully!")
        print("\nNext steps:")
        print("  1. Verify data in PostgreSQL database")
        print("  2. Start backend API: cd backend && uvicorn app.main:app --reload")
        print("  3. Start frontend: cd frontend && npm run dev")
        print("  4. Access application at http://localhost:5173")
    else:
        print(f"\n⚠ {total_count - success_count} step(s) failed. Check logs for details.")
        print(f"Log file: {log_file}")
        sys.exit(1)
    
    print("\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
