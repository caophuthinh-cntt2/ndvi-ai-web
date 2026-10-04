"""
Generate NDVI forecasts using trained Random Forest model.

Implements recursive forecasting strategy for multi-step ahead predictions.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from typing import Dict, List
import joblib
from datetime import datetime, timedelta

from feature_engineering import get_feature_names, engineer_features


def load_model(model_path: str):
    """
    Load trained model from file.
    
    Args:
        model_path: Path to saved model
    
    Returns:
        Loaded model
    """
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    model = joblib.load(model_path)
    print(f"✓ Loaded model from {model_path}")
    return model


def load_last_observations(
    data_path: str,
    n_months: int = 12
) -> pd.DataFrame:
    """
    Load last n months of observations for forecasting.
    
    Args:
        data_path: Path to prepared dataset
        n_months: Number of months to load
    
    Returns:
        DataFrame with last observations
    """
    df = pd.read_csv(data_path, parse_dates=['observation_date'])
    df = df.sort_values('observation_date')
    
    # Get last n_months
    df_last = df.tail(n_months).copy()
    
    print(f"✓ Loaded last {len(df_last)} observations")
    print(f"  Date range: {df_last['observation_date'].min()} to {df_last['observation_date'].max()}")
    
    return df_last


def prepare_forecast_features(
    history: pd.DataFrame,
    forecast_date: datetime,
    target_col: str = 'NDVI_mean'
) -> pd.DataFrame:
    """
    Prepare features for a single forecast step.
    
    Args:
        history: Historical data including recent predictions
        forecast_date: Date to forecast
        target_col: Name of target column
    
    Returns:
        DataFrame with single row of features
    """
    # Sort by date
    history = history.sort_values('observation_date').reset_index(drop=True)
    
    # Get last values for lag features
    last_values = history[target_col].values
    
    # Create feature row
    month = forecast_date.month
    time_index = len(history)
    
    features = {
        'time_index': time_index,
        f'{target_col}_lag_1': last_values[-1] if len(last_values) >= 1 else np.nan,
        f'{target_col}_lag_2': last_values[-2] if len(last_values) >= 2 else np.nan,
        f'{target_col}_lag_3': last_values[-3] if len(last_values) >= 3 else np.nan,
        f'{target_col}_lag_6': last_values[-6] if len(last_values) >= 6 else np.nan,
        f'{target_col}_lag_12': last_values[-12] if len(last_values) >= 12 else np.nan,
        f'{target_col}_rolling_mean_3': np.mean(last_values[-3:]) if len(last_values) >= 3 else np.nan,
        f'{target_col}_rolling_mean_6': np.mean(last_values[-6:]) if len(last_values) >= 6 else np.nan,
        f'{target_col}_rolling_mean_12': np.mean(last_values[-12:]) if len(last_values) >= 12 else np.nan,
        f'{target_col}_rolling_std_3': np.std(last_values[-3:]) if len(last_values) >= 3 else np.nan,
        'seasonal_sin': np.sin(2 * np.pi * month / 12),
        'seasonal_cos': np.cos(2 * np.pi * month / 12),
    }
    
    return pd.DataFrame([features])


def forecast_recursive(
    model,
    last_observations: pd.DataFrame,
    num_months: int = 12,
    target_col: str = 'NDVI_mean'
) -> pd.DataFrame:
    """
    Generate recursive multi-step forecasts.
    
    Strategy:
    1. Start with last observations from training data
    2. Predict month 1
    3. Append prediction to history
    4. Use updated history (including prediction) to predict month 2
    5. Repeat for all forecast months
    
    Args:
        model: Trained forecasting model
        last_observations: Recent historical observations
        num_months: Number of months to forecast
        target_col: Name of target column
    
    Returns:
        DataFrame with forecast results
    """
    print(f"\n{'='*70}")
    print(f"Recursive Forecasting - {num_months} Months Ahead")
    print(f"{'='*70}")
    
    # Initialize history with last observations
    history = last_observations[[target_col, 'observation_date']].copy()
    history = history.sort_values('observation_date').reset_index(drop=True)
    
    # Get last date and determine forecast dates
    last_date = history['observation_date'].max()
    forecast_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=num_months,
        freq='MS'  # Month start
    )
    
    print(f"Last historical date: {last_date.strftime('%Y-%m-%d')}")
    print(f"Forecast period: {forecast_dates[0].strftime('%Y-%m-%d')} to {forecast_dates[-1].strftime('%Y-%m-%d')}")
    print()
    
    forecasts = []
    
    for i, forecast_date in enumerate(forecast_dates):
        # Prepare features using current history
        X_forecast = prepare_forecast_features(history, forecast_date, target_col)
        
        # Make prediction
        prediction = model.predict(X_forecast)[0]
        
        # Store forecast
        forecasts.append({
            'forecast_date': forecast_date,
            'predicted_ndvi': prediction,
            'month': forecast_date.month,
            'year': forecast_date.year
        })
        
        print(f"Month {i+1:2d} ({forecast_date.strftime('%Y-%m')}): {prediction:.4f}")
        
        # Append prediction to history for next iteration
        new_row = pd.DataFrame({
            target_col: [prediction],
            'observation_date': [forecast_date]
        })
        history = pd.concat([history, new_row], ignore_index=True)
    
    print()
    return pd.DataFrame(forecasts)


def compare_with_reference(
    forecast_df: pd.DataFrame,
    reference_values: List[float] = None
) -> pd.DataFrame:
    """
    Compare generated forecasts with reference values from audit report.
    
    Args:
        forecast_df: DataFrame with generated forecasts
        reference_values: List of reference forecast values (from audit report)
    
    Returns:
        DataFrame with comparison
    """
    if reference_values is None:
        # Reference values from audit report
        reference_values = [
            0.5347, 0.5247, 0.5250, 0.5333, 0.5488, 0.5679,
            0.5736, 0.5762, 0.5705, 0.5772, 0.5713, 0.5618
        ]
    
    comparison = forecast_df.copy()
    comparison['reference_ndvi'] = reference_values[:len(forecast_df)]
    comparison['difference'] = comparison['predicted_ndvi'] - comparison['reference_ndvi']
    comparison['abs_difference'] = comparison['difference'].abs()
    
    return comparison


def save_forecast(
    forecast_df: pd.DataFrame,
    output_path: str,
    include_metadata: bool = True
):
    """
    Save forecast results to CSV.
    
    Args:
        forecast_df: DataFrame with forecast results
        output_path: Path to save CSV
        include_metadata: Whether to save metadata JSON
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    forecast_df.to_csv(output_file, index=False)
    print(f"✓ Saved forecast to {output_file}")
    
    if include_metadata:
        metadata = {
            'n_months': len(forecast_df),
            'date_range': {
                'start': forecast_df['forecast_date'].min().strftime('%Y-%m-%d'),
                'end': forecast_df['forecast_date'].max().strftime('%Y-%m-%d')
            },
            'mean_predicted_ndvi': float(forecast_df['predicted_ndvi'].mean()),
            'min_predicted_ndvi': float(forecast_df['predicted_ndvi'].min()),
            'max_predicted_ndvi': float(forecast_df['predicted_ndvi'].max()),
            'generated_at': datetime.now().isoformat()
        }
        
        metadata_path = output_file.parent / (output_file.stem + '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Saved metadata to {metadata_path}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("NDVI FORECASTING - GENERATE PREDICTIONS")
    print("=" * 70)
    
    # Load trained model
    model_path = "D:/NDVI/data/models/random_forest_final.joblib"
    
    if not Path(model_path).exists():
        print(f"\n❌ Error: Model not found at {model_path}")
        print("Please run train_model.py first.")
        sys.exit(1)
    
    model = load_model(model_path)
    
    # Load prepared dataset (for last observations)
    data_path = "D:/NDVI/data/processed/training_dataset_prepared.csv"
    
    if not Path(data_path).exists():
        print(f"\n❌ Error: Training dataset not found at {data_path}")
        print("Please run prepare_training_data.py first.")
        sys.exit(1)
    
    # Load last observations (we need at least 12 months for lag features)
    last_observations = load_last_observations(data_path, n_months=24)
    
    # Generate forecasts for 2026 (12 months)
    forecast_df = forecast_recursive(
        model,
        last_observations,
        num_months=12,
        target_col='NDVI_mean'
    )
    
    # Save forecast
    output_path = "D:/NDVI/data/processed/forecast_2026_generated.csv"
    save_forecast(forecast_df, output_path)
    
    # Compare with reference values from audit report
    print("\n" + "="*70)
    print("COMPARISON WITH REFERENCE VALUES")
    print("="*70)
    
    comparison_df = compare_with_reference(forecast_df)
    
    print(f"\n{'Month':<10} {'Generated':<12} {'Reference':<12} {'Difference':<12}")
    print("-"*70)
    for _, row in comparison_df.iterrows():
        month_str = row['forecast_date'].strftime('%Y-%m')
        print(f"{month_str:<10} {row['predicted_ndvi']:>11.4f} {row['reference_ndvi']:>11.4f} {row['difference']:>11.4f}")
    
    print("-"*70)
    print(f"Mean Absolute Difference: {comparison_df['abs_difference'].mean():.6f}")
    print(f"Max Absolute Difference:  {comparison_df['abs_difference'].max():.6f}")
    
    # Save comparison
    comparison_path = "D:/NDVI/data/processed/forecast_2026_comparison.csv"
    comparison_df.to_csv(comparison_path, index=False)
    print(f"\n✓ Saved comparison to {comparison_path}")
    
    print("\n" + "="*70)
    print("✅ FORECAST GENERATION COMPLETE!")
    print("="*70)
    print(f"\nForecast summary:")
    print(f"  Period: 2026-01 to 2026-12")
    print(f"  Mean NDVI: {forecast_df['predicted_ndvi'].mean():.4f}")
    print(f"  Min NDVI:  {forecast_df['predicted_ndvi'].min():.4f}")
    print(f"  Max NDVI:  {forecast_df['predicted_ndvi'].max():.4f}")


if __name__ == "__main__":
    main()
