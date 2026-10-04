"""
Feature engineering module for NDVI forecasting.

Creates lag features, rolling statistics, and seasonal features
with proper shifting to avoid data leakage.
"""

import pandas as pd
import numpy as np
from typing import List


def create_lag_features(df: pd.DataFrame, target_col: str, lags: List[int] = [1, 2, 3, 6, 12]) -> pd.DataFrame:
    """
    Create lag features for the target column.
    
    Args:
        df: DataFrame with time series data
        target_col: Name of the target column
        lags: List of lag periods (in months)
    
    Returns:
        DataFrame with lag features added
    """
    df = df.copy()
    
    for lag in lags:
        df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
    
    return df


def create_rolling_features(
    df: pd.DataFrame, 
    target_col: str, 
    windows: List[int] = [3, 6, 12]
) -> pd.DataFrame:
    """
    Create rolling mean and std features with proper shifting.
    
    IMPORTANT: Rolling features must be shifted by 1 to avoid data leakage.
    The rolling mean at time t should only use data from t-window to t-1.
    
    Args:
        df: DataFrame with time series data
        target_col: Name of the target column
        windows: List of window sizes (in months)
    
    Returns:
        DataFrame with rolling features added
    """
    df = df.copy()
    
    for window in windows:
        # Calculate rolling mean and shift by 1 to avoid leakage
        df[f'{target_col}_rolling_mean_{window}'] = (
            df[target_col].rolling(window=window, min_periods=1).mean().shift(1)
        )
    
    # Rolling std for 3-month window
    if 3 in windows:
        df[f'{target_col}_rolling_std_3'] = (
            df[target_col].rolling(window=3, min_periods=1).std().shift(1)
        )
    
    return df


def create_seasonal_features(df: pd.DataFrame, date_col: str = 'observation_date') -> pd.DataFrame:
    """
    Create seasonal features using sine and cosine transformations.
    
    Args:
        df: DataFrame with time series data
        date_col: Name of the date column
    
    Returns:
        DataFrame with seasonal features added
    """
    df = df.copy()
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Extract month
    month = df[date_col].dt.month
    
    # Create sine and cosine features (period = 12 months)
    df['seasonal_sin'] = np.sin(2 * np.pi * month / 12)
    df['seasonal_cos'] = np.cos(2 * np.pi * month / 12)
    
    return df


def create_time_index(df: pd.DataFrame, date_col: str = 'observation_date') -> pd.DataFrame:
    """
    Create a numeric time index (months since start).
    
    Args:
        df: DataFrame with time series data
        date_col: Name of the date column
    
    Returns:
        DataFrame with time_index added
    """
    df = df.copy()
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Create time index (months since first observation)
    df = df.sort_values(date_col).reset_index(drop=True)
    df['time_index'] = range(len(df))
    
    return df


def engineer_features(
    df: pd.DataFrame, 
    target_col: str = 'NDVI_mean',
    date_col: str = 'observation_date',
    lags: List[int] = [1, 2, 3, 6, 12],
    windows: List[int] = [3, 6, 12]
) -> pd.DataFrame:
    """
    Apply all feature engineering steps.
    
    Args:
        df: DataFrame with time series data (must have date_col and target_col)
        target_col: Name of the target column
        date_col: Name of the date column
        lags: List of lag periods
        windows: List of rolling window sizes
    
    Returns:
        DataFrame with all features engineered
    """
    df = df.copy()
    
    # Ensure sorted by date
    df = df.sort_values(date_col).reset_index(drop=True)
    
    # Create all features
    df = create_time_index(df, date_col)
    df = create_lag_features(df, target_col, lags)
    df = create_rolling_features(df, target_col, windows)
    df = create_seasonal_features(df, date_col)
    
    return df


def get_feature_names(target_col: str = 'NDVI_mean') -> List[str]:
    """
    Get list of feature column names (excluding target).
    
    Args:
        target_col: Name of the target column
    
    Returns:
        List of feature column names
    """
    features = [
        'time_index',
        f'{target_col}_lag_1',
        f'{target_col}_lag_2',
        f'{target_col}_lag_3',
        f'{target_col}_lag_6',
        f'{target_col}_lag_12',
        f'{target_col}_rolling_mean_3',
        f'{target_col}_rolling_mean_6',
        f'{target_col}_rolling_mean_12',
        f'{target_col}_rolling_std_3',
        'seasonal_sin',
        'seasonal_cos',
    ]
    
    return features


def prepare_train_test_split(
    df: pd.DataFrame,
    target_col: str = 'NDVI_mean',
    test_start_index: int = None
) -> tuple:
    """
    Split data into train and test sets, dropping rows with NaN.
    
    Args:
        df: DataFrame with engineered features
        target_col: Name of the target column
        test_start_index: Index to start test set (None = no split)
    
    Returns:
        X_train, X_test, y_train, y_test (or X, y if no split)
    """
    feature_names = get_feature_names(target_col)
    
    # Drop rows with NaN (from lag/rolling features)
    df_clean = df.dropna()
    
    X = df_clean[feature_names]
    y = df_clean[target_col]
    
    if test_start_index is None:
        return X, y
    
    # Split based on index
    X_train = X.iloc[:test_start_index]
    X_test = X.iloc[test_start_index:]
    y_train = y.iloc[:test_start_index]
    y_test = y.iloc[test_start_index:]
    
    return X_train, X_test, y_train, y_test
