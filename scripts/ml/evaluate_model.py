"""
Evaluate trained models and generate visualization plots.

Creates diagnostic plots for model performance assessment.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import joblib
import json

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


def plot_walk_forward_results(results: dict, output_dir: str):
    """
    Plot validation results over time for all models.
    
    Args:
        results: Dictionary with validation results from train_model.py
        output_dir: Directory to save plots
    """
    print("\n📊 Generating walk-forward validation plots...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extract year-by-year results for tree-based models
    models_with_years = {
        name: res for name, res in results.items()
        if 'year_results' in res and res['year_results']
    }
    
    if not models_with_years:
        print("⚠ No year-by-year results available for plotting")
        return
    
    # Create figure with subplots for each metric
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('Walk-Forward Validation Results (2020-2025)', fontsize=14, fontweight='bold')
    
    metrics = ['MAE', 'RMSE', 'R2']
    metric_labels = ['MAE', 'RMSE', 'R²']
    
    for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
        ax = axes[idx]
        
        for model_name, result in models_with_years.items():
            years = [yr['year'] for yr in result['year_results']]
            values = [yr['metrics'][metric] for yr in result['year_results']]
            
            ax.plot(years, values, marker='o', label=model_name, linewidth=2)
        
        ax.set_xlabel('Year')
        ax.set_ylabel(label)
        ax.set_title(f'{label} by Validation Year')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_file = output_path / 'walk_forward_results.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved to {output_file}")
    plt.close()


def plot_feature_importance(model, feature_names: list, output_dir: str):
    """
    Plot feature importance from trained model.
    
    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names
        output_dir: Directory to save plots
    """
    print("\n📊 Generating feature importance plot...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not hasattr(model, 'feature_importances_'):
        print("⚠ Model does not have feature_importances_ attribute")
        return
    
    # Create DataFrame
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.barplot(
        data=importance_df,
        x='importance',
        y='feature',
        ax=ax,
        palette='viridis'
    )
    
    ax.set_title('Feature Importance - Random Forest Model', fontsize=14, fontweight='bold')
    ax.set_xlabel('Importance')
    ax.set_ylabel('Feature')
    
    plt.tight_layout()
    
    output_file = output_path / 'feature_importance.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved to {output_file}")
    plt.close()


def plot_predictions_vs_actual(results: dict, output_dir: str):
    """
    Plot predictions vs actual values for all models.
    
    Args:
        results: Dictionary with validation results
        output_dir: Directory to save plots
    """
    print("\n📊 Generating predictions vs actual plots...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extract models with predictions
    models_with_preds = {
        name: res for name, res in results.items()
        if 'predictions' in res and res['predictions']
    }
    
    if not models_with_preds:
        print("⚠ No predictions available for plotting")
        return
    
    # Create subplot for each model
    n_models = len(models_with_preds)
    fig, axes = plt.subplots(1, n_models, figsize=(6*n_models, 5))
    
    if n_models == 1:
        axes = [axes]
    
    fig.suptitle('Predictions vs Actual Values (Validation Set)', fontsize=14, fontweight='bold')
    
    for idx, (model_name, result) in enumerate(models_with_preds.items()):
        ax = axes[idx]
        
        y_true = result['predictions']['y_true']
        y_pred = result['predictions']['y_pred']
        
        # Scatter plot
        ax.scatter(y_true, y_pred, alpha=0.6, s=50)
        
        # Perfect prediction line
        min_val = min(min(y_true), min(y_pred))
        max_val = max(max(y_true), max(y_pred))
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        
        # Metrics
        metrics = result['overall_metrics']
        textstr = f"MAE: {metrics['MAE']:.4f}\nRMSE: {metrics['RMSE']:.4f}\nR²: {metrics['R2']:.4f}"
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('Actual NDVI')
        ax.set_ylabel('Predicted NDVI')
        ax.set_title(model_name)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_file = output_path / 'predictions_vs_actual.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved to {output_file}")
    plt.close()


def plot_model_comparison_bar(results: dict, output_dir: str):
    """
    Bar chart comparing model performance metrics.
    
    Args:
        results: Dictionary with validation results
        output_dir: Directory to save plots
    """
    print("\n📊 Generating model comparison bar chart...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extract metrics
    comparison_data = []
    for model_name, result in results.items():
        metrics = result['overall_metrics']
        comparison_data.append({
            'Model': model_name,
            'MAE': metrics['MAE'],
            'RMSE': metrics['RMSE'],
            'R2': metrics['R2']
        })
    
    df = pd.DataFrame(comparison_data)
    
    # Create subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Model Performance Comparison', fontsize=14, fontweight='bold')
    
    # MAE
    sns.barplot(data=df, x='Model', y='MAE', ax=axes[0], palette='Set2')
    axes[0].set_title('Mean Absolute Error (lower is better)')
    axes[0].set_ylabel('MAE')
    axes[0].tick_params(axis='x', rotation=45)
    
    # RMSE
    sns.barplot(data=df, x='Model', y='RMSE', ax=axes[1], palette='Set2')
    axes[1].set_title('Root Mean Squared Error (lower is better)')
    axes[1].set_ylabel('RMSE')
    axes[1].tick_params(axis='x', rotation=45)
    
    # R²
    sns.barplot(data=df, x='Model', y='R2', ax=axes[2], palette='Set2')
    axes[2].set_title('R² Score (higher is better)')
    axes[2].set_ylabel('R²')
    axes[2].axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    output_file = output_path / 'model_comparison_bar.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved to {output_file}")
    plt.close()


def plot_forecast_comparison(output_dir: str):
    """
    Plot generated forecasts vs reference values.
    
    Args:
        output_dir: Directory to save plots
    """
    print("\n📊 Generating forecast comparison plot...")
    
    comparison_path = "D:/NDVI/data/processed/forecast_2026_comparison.csv"
    
    if not Path(comparison_path).exists():
        print(f"⚠ Comparison file not found: {comparison_path}")
        return
    
    df = pd.read_csv(comparison_path, parse_dates=['forecast_date'])
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle('2026 NDVI Forecast Comparison', fontsize=14, fontweight='bold')
    
    # Plot 1: Forecasts comparison
    ax1 = axes[0]
    ax1.plot(df['forecast_date'], df['predicted_ndvi'], marker='o', label='Generated Forecast', linewidth=2)
    ax1.plot(df['forecast_date'], df['reference_ndvi'], marker='s', label='Reference Forecast', linewidth=2)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('NDVI')
    ax1.set_title('Generated vs Reference Forecasts')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Differences
    ax2 = axes[1]
    ax2.bar(df['forecast_date'], df['difference'], alpha=0.7, color='steelblue')
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Difference (Generated - Reference)')
    ax2.set_title('Forecast Differences')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_file = output_path / 'forecast_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved to {output_file}")
    plt.close()


def generate_summary_report(results: dict, output_dir: str):
    """
    Generate text summary report.
    
    Args:
        results: Dictionary with validation results
        output_dir: Directory to save report
    """
    print("\n📝 Generating summary report...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_lines = []
    report_lines.append("="*70)
    report_lines.append("NDVI FORECASTING MODEL EVALUATION REPORT")
    report_lines.append("="*70)
    report_lines.append("")
    report_lines.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    report_lines.append("="*70)
    report_lines.append("MODEL PERFORMANCE SUMMARY")
    report_lines.append("="*70)
    report_lines.append("")
    report_lines.append(f"{'Model':<25} {'MAE':>12} {'RMSE':>12} {'R²':>12}")
    report_lines.append("-"*70)
    
    for model_name, result in results.items():
        metrics = result['overall_metrics']
        report_lines.append(
            f"{model_name:<25} {metrics['MAE']:>12.6f} {metrics['RMSE']:>12.6f} {metrics['R2']:>12.6f}"
        )
    
    report_lines.append("="*70)
    report_lines.append("")
    
    # Best model
    best_model = min(results.items(), key=lambda x: x[1]['overall_metrics']['MAE'])
    report_lines.append("BEST MODEL (by MAE):")
    report_lines.append(f"  {best_model[0]}")
    report_lines.append(f"  MAE: {best_model[1]['overall_metrics']['MAE']:.6f}")
    report_lines.append(f"  RMSE: {best_model[1]['overall_metrics']['RMSE']:.6f}")
    report_lines.append(f"  R²: {best_model[1]['overall_metrics']['R2']:.6f}")
    report_lines.append("")
    
    # Year-by-year results for Random Forest
    if 'Random Forest' in results and 'year_results' in results['Random Forest']:
        report_lines.append("="*70)
        report_lines.append("RANDOM FOREST - YEAR-BY-YEAR VALIDATION")
        report_lines.append("="*70)
        report_lines.append("")
        report_lines.append(f"{'Year':<10} {'MAE':>12} {'RMSE':>12} {'R²':>12} {'Train Size':>12} {'Test Size':>12}")
        report_lines.append("-"*70)
        
        for yr in results['Random Forest']['year_results']:
            report_lines.append(
                f"{yr['year']:<10} "
                f"{yr['metrics']['MAE']:>12.6f} "
                f"{yr['metrics']['RMSE']:>12.6f} "
                f"{yr['metrics']['R2']:>12.6f} "
                f"{yr['n_train']:>12} "
                f"{yr['n_test']:>12}"
            )
        
        report_lines.append("")
    
    report_lines.append("="*70)
    report_lines.append("END OF REPORT")
    report_lines.append("="*70)
    
    # Save report
    report_text = "\n".join(report_lines)
    output_file = output_path / 'evaluation_report.txt'
    
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    print(f"✓ Saved to {output_file}")
    
    # Also print to console
    print("\n" + report_text)


def main():
    """Main execution function."""
    print("=" * 70)
    print("NDVI FORECASTING - MODEL EVALUATION")
    print("=" * 70)
    
    # Load validation results
    results_path = "D:/NDVI/data/models/validation_results.pkl"
    
    if not Path(results_path).exists():
        print(f"\n❌ Error: Validation results not found at {results_path}")
        print("Please run train_model.py first.")
        sys.exit(1)
    
    results = joblib.load(results_path)
    print(f"✓ Loaded validation results")
    
    # Output directory
    output_dir = "D:/NDVI/data/processed/evaluation"
    
    # Generate all plots
    plot_walk_forward_results(results, output_dir)
    plot_predictions_vs_actual(results, output_dir)
    plot_model_comparison_bar(results, output_dir)
    
    # Load and plot feature importance
    model_path = "D:/NDVI/data/models/random_forest_final.joblib"
    if Path(model_path).exists():
        model = joblib.load(model_path)
        
        # Get feature names
        from feature_engineering import get_feature_names
        feature_names = get_feature_names('NDVI_mean')
        
        plot_feature_importance(model, feature_names, output_dir)
    
    # Plot forecast comparison (if available)
    plot_forecast_comparison(output_dir)
    
    # Generate summary report
    generate_summary_report(results, output_dir)
    
    print("\n" + "="*70)
    print("✅ MODEL EVALUATION COMPLETE!")
    print("="*70)
    print(f"\nAll plots and reports saved to: {output_dir}")


if __name__ == "__main__":
    main()
