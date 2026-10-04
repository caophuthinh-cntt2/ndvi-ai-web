"""
Train NDVI forecasting models with walk-forward validation.

Implements Random Forest, Extra Trees, Hist Gradient Boosting,
and Seasonal Naive baseline models.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import sys
from typing import Dict, Tuple, List
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    HistGradientBoostingRegressor
)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

from feature_engineering import get_feature_names
from seasonal_naive import seasonal_naive_validate


def expanding_walk_forward_validation(
    df: pd.DataFrame,
    target_col: str = 'NDVI_mean',
    start_year: int = 2020,
    end_year: int = 2025
) -> List[Tuple[pd.DataFrame, pd.DataFrame, int]]:
    """
    Generate expanding window walk-forward validation splits.
    
    For each year from start_year to end_year:
      - Train: all data from beginning up to (year - 1)
      - Test: all data in year
    
    Args:
        df: DataFrame with engineered features
        target_col: Name of target column
        start_year: First validation year
        end_year: Last validation year
    
    Returns:
        List of (train_df, test_df, year) tuples
    """
    df = df.copy()
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    df = df.sort_values('observation_date').reset_index(drop=True)
    
    # Remove rows with NaN
    df = df.dropna()
    
    splits = []
    
    for year in range(start_year, end_year + 1):
        # Train: up to end of previous year
        train_mask = df['observation_date'].dt.year < year
        # Test: current year
        test_mask = df['observation_date'].dt.year == year
        
        train_df = df[train_mask]
        test_df = df[test_mask]
        
        if len(train_df) > 0 and len(test_df) > 0:
            splits.append((train_df, test_df, year))
            print(f"  Year {year}: Train size = {len(train_df)}, Test size = {len(test_df)}")
    
    return splits


def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    params: dict = None
) -> RandomForestRegressor:
    """
    Train Random Forest model.
    
    Args:
        X_train: Training features
        y_train: Training target
        params: Model hyperparameters
    
    Returns:
        Trained Random Forest model
    """
    if params is None:
        params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_jobs': -1
        }
    
    model = RandomForestRegressor(**params)
    model.fit(X_train, y_train)
    
    return model


def train_extra_trees(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    params: dict = None
) -> ExtraTreesRegressor:
    """
    Train Extra Trees model.
    
    Args:
        X_train: Training features
        y_train: Training target
        params: Model hyperparameters
    
    Returns:
        Trained Extra Trees model
    """
    if params is None:
        params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_jobs': -1
        }
    
    model = ExtraTreesRegressor(**params)
    model.fit(X_train, y_train)
    
    return model


def train_hist_gradient_boosting(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    params: dict = None
) -> HistGradientBoostingRegressor:
    """
    Train Hist Gradient Boosting model.
    
    Args:
        X_train: Training features
        y_train: Training target
        params: Model hyperparameters
    
    Returns:
        Trained Hist Gradient Boosting model
    """
    if params is None:
        params = {
            'max_iter': 100,
            'max_depth': 10,
            'learning_rate': 0.1,
            'random_state': 42
        }
    
    model = HistGradientBoostingRegressor(**params)
    model.fit(X_train, y_train)
    
    return model


def evaluate_model(y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate regression metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Dictionary with MAE, RMSE, R² metrics
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2
    }


def walk_forward_validation_single_model(
    df: pd.DataFrame,
    model_name: str,
    model_fn,
    params: dict = None,
    target_col: str = 'NDVI_mean',
    start_year: int = 2020,
    end_year: int = 2025
) -> Dict:
    """
    Run walk-forward validation for a single model.
    
    Args:
        df: DataFrame with engineered features
        model_name: Name of the model
        model_fn: Function to train the model
        params: Model hyperparameters
        target_col: Name of target column
        start_year: First validation year
        end_year: Last validation year
    
    Returns:
        Dictionary with validation results
    """
    print(f"\n{'='*70}")
    print(f"Walk-Forward Validation: {model_name}")
    print(f"{'='*70}")
    
    feature_names = get_feature_names(target_col)
    splits = expanding_walk_forward_validation(df, target_col, start_year, end_year)
    
    year_results = []
    all_y_true = []
    all_y_pred = []
    
    for train_df, test_df, year in splits:
        print(f"\nValidating year {year}...")
        
        X_train = train_df[feature_names]
        y_train = train_df[target_col]
        X_test = test_df[feature_names]
        y_test = test_df[target_col]
        
        # Train model
        model = model_fn(X_train, y_train, params)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Evaluate
        metrics = evaluate_model(y_test, y_pred)
        
        print(f"  MAE: {metrics['MAE']:.6f}")
        print(f"  RMSE: {metrics['RMSE']:.6f}")
        print(f"  R²: {metrics['R2']:.6f}")
        
        year_results.append({
            'year': year,
            'metrics': metrics,
            'n_train': len(train_df),
            'n_test': len(test_df)
        })
        
        all_y_true.extend(y_test.values)
        all_y_pred.extend(y_pred)
    
    # Calculate overall metrics
    overall_metrics = evaluate_model(
        pd.Series(all_y_true),
        np.array(all_y_pred)
    )
    
    print(f"\n{'='*70}")
    print(f"Overall Metrics ({start_year}-{end_year}):")
    print(f"  MAE: {overall_metrics['MAE']:.6f}")
    print(f"  RMSE: {overall_metrics['RMSE']:.6f}")
    print(f"  R²: {overall_metrics['R2']:.6f}")
    print(f"{'='*70}")
    
    return {
        'model_name': model_name,
        'overall_metrics': overall_metrics,
        'year_results': year_results,
        'predictions': {
            'y_true': all_y_true,
            'y_pred': all_y_pred
        }
    }


def compare_models(
    df: pd.DataFrame,
    target_col: str = 'NDVI_mean',
    start_year: int = 2020,
    end_year: int = 2025
) -> Dict:
    """
    Compare multiple models using walk-forward validation.
    
    Args:
        df: DataFrame with engineered features
        target_col: Name of target column
        start_year: First validation year
        end_year: Last validation year
    
    Returns:
        Dictionary with comparison results
    """
    print("\n" + "="*70)
    print("MODEL COMPARISON - WALK-FORWARD VALIDATION")
    print("="*70)
    
    results = {}
    
    # 1. Random Forest
    results['Random Forest'] = walk_forward_validation_single_model(
        df, 'Random Forest', train_random_forest, target_col=target_col,
        start_year=start_year, end_year=end_year
    )
    
    # 2. Extra Trees
    results['Extra Trees'] = walk_forward_validation_single_model(
        df, 'Extra Trees', train_extra_trees, target_col=target_col,
        start_year=start_year, end_year=end_year
    )
    
    # 3. Hist Gradient Boosting
    results['HistGradientBoosting'] = walk_forward_validation_single_model(
        df, 'HistGradientBoosting', train_hist_gradient_boosting,
        target_col=target_col, start_year=start_year, end_year=end_year
    )
    
    # 4. Seasonal Naive (baseline)
    print(f"\n{'='*70}")
    print(f"Walk-Forward Validation: Seasonal Naive")
    print(f"{'='*70}")
    
    naive_metrics = seasonal_naive_validate(df, target_col, start_year, end_year)
    
    print(f"\nOverall Metrics ({start_year}-{end_year}):")
    print(f"  MAE: {naive_metrics['MAE']:.6f}")
    print(f"  RMSE: {naive_metrics['RMSE']:.6f}")
    print(f"  R²: {naive_metrics['R2']:.6f}")
    print(f"{'='*70}")
    
    results['Seasonal Naive'] = {
        'model_name': 'Seasonal Naive',
        'overall_metrics': naive_metrics
    }
    
    # Print comparison table
    print("\n" + "="*70)
    print("MODEL COMPARISON SUMMARY")
    print("="*70)
    print(f"{'Model':<25} {'MAE':>12} {'RMSE':>12} {'R²':>12}")
    print("-"*70)
    
    for model_name, result in results.items():
        metrics = result['overall_metrics']
        print(f"{model_name:<25} {metrics['MAE']:>12.6f} {metrics['RMSE']:>12.6f} {metrics['R2']:>12.6f}")
    
    print("="*70)
    
    return results


def train_final_model(
    df: pd.DataFrame,
    target_col: str = 'NDVI_mean',
    model_type: str = 'random_forest'
) -> Tuple[object, Dict]:
    """
    Train final model on full dataset.
    
    Args:
        df: DataFrame with engineered features
        target_col: Name of target column
        model_type: Type of model to train
    
    Returns:
        Tuple of (trained_model, feature_importance_dict)
    """
    print(f"\n{'='*70}")
    print(f"Training Final Model: {model_type}")
    print(f"{'='*70}")
    
    feature_names = get_feature_names(target_col)
    
    # Remove NaN
    df_clean = df.dropna()
    
    X = df_clean[feature_names]
    y = df_clean[target_col]
    
    print(f"Training set size: {len(X)}")
    print(f"Features: {len(feature_names)}")
    
    # Train model
    if model_type == 'random_forest':
        model = train_random_forest(X, y)
    elif model_type == 'extra_trees':
        model = train_extra_trees(X, y)
    elif model_type == 'hist_gradient_boosting':
        model = train_hist_gradient_boosting(X, y)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Get feature importance
    if hasattr(model, 'feature_importances_'):
        feature_importance = {
            name: float(importance)
            for name, importance in zip(feature_names, model.feature_importances_)
        }
        
        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        print("\nFeature Importance (Top 5):")
        for i, (name, importance) in enumerate(list(feature_importance.items())[:5]):
            print(f"  {i+1}. {name}: {importance:.4f}")
    else:
        feature_importance = {}
    
    print(f"\n✓ Model trained successfully")
    
    return model, feature_importance


def main():
    """Main execution function."""
    print("=" * 70)
    print("NDVI FORECASTING - MODEL TRAINING")
    print("=" * 70)
    
    # Load prepared dataset
    data_path = "D:/NDVI/data/processed/training_dataset_prepared.csv"
    
    if not Path(data_path).exists():
        print(f"\n❌ Error: Training dataset not found at {data_path}")
        print("Please run prepare_training_data.py first.")
        sys.exit(1)
    
    df = pd.read_csv(data_path, parse_dates=['observation_date'])
    print(f"\n✓ Loaded prepared dataset: {df.shape}")
    
    # Check if we have enough data
    df_clean = df.dropna()
    if len(df_clean) < 24:
        print(f"\n⚠ WARNING: Only {len(df_clean)} valid observations.")
        print("Need at least 24 observations for meaningful validation.")
        
        if len(df_clean) == 0:
            print("\n❌ No valid data available. Cannot train models.")
            sys.exit(1)
    
    # Run model comparison with walk-forward validation
    comparison_results = compare_models(df, target_col='NDVI_mean', start_year=2020, end_year=2025)
    
    # Save comparison results
    models_dir = Path("D:/NDVI/data/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Save metrics (without predictions arrays for JSON serialization)
    metrics_only = {}
    for model_name, result in comparison_results.items():
        metrics_only[model_name] = result['overall_metrics']
    
    metrics_path = models_dir / "metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics_only, f, indent=2)
    print(f"\n✓ Saved metrics to {metrics_path}")
    
    # Save full results (with predictions)
    results_path = models_dir / "validation_results.pkl"
    joblib.dump(comparison_results, results_path)
    print(f"✓ Saved full results to {results_path}")
    
    # Train final Random Forest model on full data
    final_model, feature_importance = train_final_model(df, target_col='NDVI_mean', model_type='random_forest')
    
    # Save final model
    model_path = models_dir / "random_forest_final.joblib"
    joblib.dump(final_model, model_path)
    print(f"✓ Saved final model to {model_path}")
    
    # Save feature importance
    importance_path = models_dir / "feature_importance.json"
    with open(importance_path, 'w') as f:
        json.dump(feature_importance, f, indent=2)
    print(f"✓ Saved feature importance to {importance_path}")
    
    # Also train and save other models
    print("\n" + "="*70)
    print("Training additional models on full dataset...")
    print("="*70)
    
    extra_trees_model, _ = train_final_model(df, target_col='NDVI_mean', model_type='extra_trees')
    extra_trees_path = models_dir / "extra_trees_final.joblib"
    joblib.dump(extra_trees_model, extra_trees_path)
    print(f"✓ Saved Extra Trees model to {extra_trees_path}")
    
    hist_gb_model, _ = train_final_model(df, target_col='NDVI_mean', model_type='hist_gradient_boosting')
    hist_gb_path = models_dir / "hist_gradient_boosting_final.joblib"
    joblib.dump(hist_gb_model, hist_gb_path)
    print(f"✓ Saved Hist Gradient Boosting model to {hist_gb_path}")
    
    print("\n" + "="*70)
    print("✅ MODEL TRAINING COMPLETE!")
    print("="*70)
    print(f"\nBest model: Random Forest")
    print(f"  MAE: {metrics_only['Random Forest']['MAE']:.6f}")
    print(f"  RMSE: {metrics_only['Random Forest']['RMSE']:.6f}")
    print(f"  R²: {metrics_only['Random Forest']['R2']:.6f}")
    print(f"\nModels saved to: {models_dir}")


if __name__ == "__main__":
    main()
