"""
Seasonal Naive Baseline Model for NDVI Forecasting.

Predicts NDVI value as the same value from 12 months ago.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def seasonal_naive_forecast(
    df: pd.DataFrame,
    target_col: str = 'NDVI_mean',
    season_length: int = 12
) -> pd.DataFrame:
    """
    Create seasonal naive forecasts (predict same as 12 months ago).
    
    Args:
        df: DataFrame with time series data
        target_col: Name of the target column
        season_length: Seasonal period (12 for monthly data)
    
    Returns:
        DataFrame with predictions
    """
    df = df.copy()
    df['seasonal_naive_pred'] = df[target_col].shift(season_length)
    
    return df


def evaluate_seasonal_naive(
    y_true: pd.Series,
    y_pred: pd.Series
) -> dict:
    """
    Evaluate seasonal naive model performance.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
    
    Returns:
        Dictionary with MAE, RMSE, R² metrics
    """
    # Remove NaN values
    mask = ~(y_true.isna() | y_pred.isna())
    y_true_clean = y_true[mask]
    y_pred_clean = y_pred[mask]
    
    mae = mean_absolute_error(y_true_clean, y_pred_clean)
    rmse = np.sqrt(mean_squared_error(y_true_clean, y_pred_clean))
    r2 = r2_score(y_true_clean, y_pred_clean)
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2
    }


def seasonal_naive_validate(
    df: pd.DataFrame,
    target_col: str = 'NDVI_mean',
    start_year: int = 2020,
    end_year: int = 2025
) -> dict:
    """
    Walk-forward validation for seasonal naive model.
    
    Args:
        df: DataFrame with time series data
        target_col: Name of the target column
        start_year: Start year for validation
        end_year: End year for validation
    
    Returns:
        Dictionary with aggregated metrics
    """
    df = df.copy()
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    df = df.sort_values('observation_date')
    
    # Create seasonal naive predictions
    df = seasonal_naive_forecast(df, target_col)
    
    # Filter to validation period
    validation_mask = (
        (df['observation_date'].dt.year >= start_year) &
        (df['observation_date'].dt.year <= end_year)
    )
    
    y_true = df.loc[validation_mask, target_col]
    y_pred = df.loc[validation_mask, 'seasonal_naive_pred']
    
    return evaluate_seasonal_naive(y_true, y_pred)
