"""
Prepare training dataset for NDVI forecasting.

Loads data from database or CSV, engineers features, and saves prepared dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from sqlalchemy import create_engine
from feature_engineering import engineer_features


def load_timeseries_from_db(database_url: str = None) -> pd.DataFrame:
    """
    Load time series data from ndvi_timeseries table.
    
    Args:
        database_url: PostgreSQL connection string
    
    Returns:
        DataFrame with time series data
    """
    if database_url is None:
        # Try to load from environment or use default
        database_url = "postgresql://ndvi_user:secure_password@localhost:5432/ndvi_db"
    
    try:
        engine = create_engine(database_url)
        
        query = """
        SELECT 
            observation_date,
            ndvi_mean as NDVI_mean
        FROM ndvi_timeseries
        WHERE source_type = 'observed'
        ORDER BY observation_date
        """
        
        df = pd.read_sql(query, engine)
        print(f"✓ Loaded {len(df)} observations from database")
        return df
        
    except Exception as e:
        print(f"⚠ Could not load from database: {e}")
        return None


def load_timeseries_from_csv(csv_path: str) -> pd.DataFrame:
    """
    Load time series data from CSV file.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        DataFrame with time series data
    """
    try:
        df = pd.read_csv(csv_path, parse_dates=['observation_date'])
        
        # Ensure required columns exist
        if 'NDVI_mean' not in df.columns:
            if 'ndvi_mean' in df.columns:
                df['NDVI_mean'] = df['ndvi_mean']
            else:
                raise ValueError("CSV must contain 'NDVI_mean' or 'ndvi_mean' column")
        
        print(f"✓ Loaded {len(df)} observations from CSV")
        return df[['observation_date', 'NDVI_mean']]
        
    except Exception as e:
        print(f"⚠ Could not load from CSV: {e}")
        return None


def create_training_schema() -> pd.DataFrame:
    """
    Create empty DataFrame with correct schema as placeholder.
    
    Returns:
        Empty DataFrame with correct column names
    """
    return pd.DataFrame({
        'observation_date': pd.to_datetime([]),
        'NDVI_mean': []
    })


def prepare_dataset(
    data_source: str = 'auto',
    csv_path: str = None,
    database_url: str = None
) -> pd.DataFrame:
    """
    Prepare training dataset with feature engineering.
    
    Args:
        data_source: 'auto', 'database', or 'csv'
        csv_path: Path to CSV file (if source='csv')
        database_url: Database connection string (if source='database')
    
    Returns:
        DataFrame with engineered features
    """
    df = None
    
    if data_source == 'auto':
        # Try database first, then CSV
        df = load_timeseries_from_db(database_url)
        
        if df is None or len(df) == 0:
            # Try default CSV locations
            csv_candidates = [
                csv_path,
                "D:/NDVI/data/processed/timeseries.csv",
                "D:/NDVI/data/timeseries.csv",
            ]
            
            for csv_file in csv_candidates:
                if csv_file and Path(csv_file).exists():
                    df = load_timeseries_from_csv(csv_file)
                    if df is not None:
                        break
    
    elif data_source == 'database':
        df = load_timeseries_from_db(database_url)
    
    elif data_source == 'csv':
        if csv_path is None:
            raise ValueError("csv_path must be provided when data_source='csv'")
        df = load_timeseries_from_csv(csv_path)
    
    else:
        raise ValueError(f"Invalid data_source: {data_source}")
    
    # If no data found, create schema placeholder
    if df is None or len(df) == 0:
        print("\n⚠ WARNING: No training data found!")
        print("Creating schema placeholder. You need to provide actual data to train the model.")
        print("\nExpected format:")
        print("  - Column 1: observation_date (YYYY-MM-DD)")
        print("  - Column 2: NDVI_mean (float)")
        print("  - 132 monthly observations from 2015-01 to 2025-12")
        print("\nSave your data to one of these locations:")
        print("  - Database: ndvi_timeseries table")
        print("  - CSV: D:/NDVI/data/processed/timeseries.csv")
        
        df = create_training_schema()
        return df
    
    # Validate data
    if len(df) < 12:
        print(f"⚠ WARNING: Only {len(df)} observations found. Need at least 12 for lag features.")
    
    # Engineer features
    print("\n🔧 Engineering features...")
    df_engineered = engineer_features(df)
    
    # Report feature engineering results
    n_original = len(df)
    n_after_features = len(df_engineered)
    n_valid = df_engineered.dropna().shape[0]
    
    print(f"  Original observations: {n_original}")
    print(f"  After feature engineering: {n_after_features}")
    print(f"  Valid (no NaN): {n_valid}")
    print(f"  Features created: {len(df_engineered.columns) - 2}")  # Exclude date and target
    
    return df_engineered


def save_prepared_dataset(df: pd.DataFrame, output_path: str):
    """
    Save prepared dataset to CSV.
    
    Args:
        df: DataFrame with engineered features
        output_path: Path to save CSV
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved prepared dataset to {output_file}")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("NDVI FORECASTING - TRAINING DATA PREPARATION")
    print("=" * 70)
    
    # Prepare dataset (auto-detect source)
    df = prepare_dataset(data_source='auto')
    
    if len(df) == 0:
        print("\n❌ No data available. Exiting.")
        print("Please provide training data before running the pipeline.")
        sys.exit(1)
    
    # Save prepared dataset
    output_path = "D:/NDVI/data/processed/training_dataset_prepared.csv"
    save_prepared_dataset(df, output_path)
    
    # Save metadata
    metadata = {
        'n_observations': len(df),
        'n_valid': df.dropna().shape[0],
        'date_range': {
            'start': str(df['observation_date'].min()),
            'end': str(df['observation_date'].max())
        },
        'features': [col for col in df.columns if col not in ['observation_date', 'NDVI_mean']],
        'target': 'NDVI_mean'
    }
    
    metadata_path = "D:/NDVI/data/processed/training_dataset_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Saved metadata to {metadata_path}")
    print("\n✅ Data preparation complete!")


if __name__ == "__main__":
    main()
