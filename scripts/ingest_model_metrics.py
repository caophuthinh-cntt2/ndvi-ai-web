#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Model Metrics
Inserts model comparison results from audit report into database
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import json

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
        logging.FileHandler(Path(__file__).parent.parent / 'data' / 'logs' / f'ingest_models_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'ndvi_ai'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )

def ingest_model_metrics(conn):
    """Insert model comparison metrics from audit report"""
    
    logger.info("="*60)
    logger.info("Ingesting Model Metrics")
    logger.info("="*60)
    
    # Model metrics from audit report
    models = [
        {
            'model_type': 'RANDOM_FOREST',
            'model_name': 'Random Forest Regressor',
            'run_name': 'random_forest_2015_2025',
            'mae': 0.021111,
            'rmse': 0.027339,
            'r2_score': 0.221221,
            'is_selected': True,
            'parameters': {
                'n_estimators': 100,
                'max_depth': None,
                'min_samples_split': 2,
                'min_samples_leaf': 1,
                'features': [
                    'lag_1', 'lag_2', 'lag_3', 'lag_6', 'lag_12',
                    'rolling_mean_3', 'rolling_mean_6', 'rolling_mean_12',
                    'rolling_std_3', 'seasonal_sin', 'seasonal_cos', 'time_index'
                ]
            },
            'notes': 'Best performing model with balanced MAE and R² score'
        },
        {
            'model_type': 'EXTRA_TREES',
            'model_name': 'Extra Trees Regressor',
            'run_name': 'extra_trees_2015_2025',
            'mae': 0.020286,
            'rmse': 0.027439,
            'r2_score': 0.193925,
            'is_selected': False,
            'parameters': {
                'n_estimators': 100,
                'max_depth': None,
                'min_samples_split': 2,
                'min_samples_leaf': 1
            },
            'notes': 'Lowest MAE but lower R² compared to Random Forest'
        },
        {
            'model_type': 'HIST_GRADIENT_BOOSTING',
            'model_name': 'HistGradientBoosting Regressor',
            'run_name': 'hist_gradient_boosting_2015_2025',
            'mae': 0.025380,
            'rmse': 0.032245,
            'r2_score': -0.293690,
            'is_selected': False,
            'parameters': {
                'max_iter': 100,
                'max_depth': None,
                'learning_rate': 0.1
            },
            'notes': 'Poor performance with negative R²'
        },
        {
            'model_type': 'SEASONAL_NAIVE',
            'model_name': 'Seasonal Naive Baseline',
            'run_name': 'seasonal_naive_baseline_2015_2025',
            'mae': 0.026834,
            'rmse': 0.036315,
            'r2_score': -0.760498,
            'is_selected': False,
            'parameters': {
                'seasonal_period': 12,
                'method': 'last_year_same_month'
            },
            'notes': 'Baseline model for comparison'
        }
    ]
    
    cursor = conn.cursor()
    inserted = 0
    
    for model in models:
        # Check if exists
        cursor.execute("""
            SELECT id FROM model_runs WHERE run_name = %s
        """, (model['run_name'],))
        
        existing = cursor.fetchone()
        
        if existing:
            logger.info(f"  Model '{model['model_name']}' already exists (ID: {existing[0]})")
            continue
        
        # Insert model run
        cursor.execute("""
            INSERT INTO model_runs (
                model_type, model_name, run_name,
                training_start_date, training_end_date, validation_method,
                mae, rmse, r2_score, parameters_json, is_selected, notes
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            model['model_type'],
            model['model_name'],
            model['run_name'],
            '2015-01-01',
            '2025-12-31',
            'expanding_walk_forward',
            model['mae'],
            model['rmse'],
            model['r2_score'],
            Json(model['parameters']),
            model['is_selected'],
            model['notes']
        ))
        
        model_id = cursor.fetchone()[0]
        logger.info(f"✓ Inserted: {model['model_name']} (ID: {model_id})")
        inserted += 1
    
    conn.commit()
    
    logger.info("="*60)
    logger.info(f"✓ Inserted {inserted} model runs")
    logger.info("="*60)
    
    return inserted

def main():
    """Main model metrics ingestion process"""
    
    print("="*60)
    print("NDVI Model Metrics Ingestion")
    print("="*60)
    
    try:
        conn = get_db_connection()
        logger.info("✓ Connected to database")
        
        ingest_model_metrics(conn)
        
        # Display summary
        cursor = conn.cursor()
        cursor.execute("""
            SELECT model_name, mae, rmse, r2_score, is_selected
            FROM model_runs
            ORDER BY mae ASC
        """)
        
        results = cursor.fetchall()
        
        print("\n" + "="*60)
        print("Model Performance Summary")
        print("="*60)
        print(f"{'Model':<40} {'MAE':<10} {'RMSE':<10} {'R²':<10} {'Selected'}")
        print("-"*60)
        
        for row in results:
            selected = "✓" if row[4] else ""
            print(f"{row[0]:<40} {row[1]:<10.6f} {row[2]:<10.6f} {row[3]:<10.6f} {selected}")
        
        print("="*60)
        
        conn.close()
        
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
