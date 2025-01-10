import pandas as pd
import numpy as np
from itertools import product
from typing import Dict, List, Tuple, Optional, Union
import sys
sys.path.append('..')
from models.trading_agent import TradingAgent

def grid_search_parameters(
    df: pd.DataFrame,
    short_windows: List[int] = [5, 10, 15, 20, 25, 30],
    long_windows: List[int] = [20, 35, 50, 75, 100, 150, 200],
    ml_weights: List[float] = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
    max_depths: List[Optional[int]] = [3, 5, 8, 10, None],
    min_samples_splits: List[int] = [2, 5, 10],
    n_estimators_list: List[int] = [50, 100, 200]
) -> Dict:
    """
    Perform grid search over strategy parameters
    
    Args:
        df: Historical price data
        short_windows: List of short MA windows to test
        long_windows: List of long MA windows to test
        ml_weights: List of ML signal weights to test
        
    Returns:
        Dict containing best parameters and their performance
    """
    best_sharpe = float('-inf')
    best_params = {}
    results = []
    
    # Generate all parameter combinations
    param_combinations = [
        (short, long, weight, max_depth, min_samples_split, n_estimators)
        for short, long, weight, max_depth, min_samples_split, n_estimators 
        in product(short_windows, long_windows, ml_weights, max_depths, min_samples_splits, n_estimators_list)
        if short < long  # Ensure short window is less than long window
    ]
    
    for short_window, long_window, ml_weight, max_depth, min_samples_split, n_estimators in param_combinations:
        print(f"\nTesting parameters: Short={short_window}, Long={long_window}, ML Weight={ml_weight}")
        
        # Initialize and train agent with ML hyperparameters
        agent = TradingAgent(
            short_window=short_window,
            long_window=long_window,
            ml_weight=ml_weight,
            ml_params={
                'max_depth': max_depth,
                'min_samples_split': min_samples_split,
                'n_estimators': n_estimators
            }
        )
        
        try:
            # Train and evaluate
            train_metrics = agent.train(df)
            performance = agent.backtest(df)
            
            results.append({
                'short_window': short_window,
                'long_window': long_window,
                'ml_weight': ml_weight,
                'sharpe_ratio': performance['sharpe_ratio'],
                'total_return': performance['total_return'],
                'max_drawdown': performance['max_drawdown'],
                'train_accuracy': train_metrics['train_accuracy'],
                'test_accuracy': train_metrics['test_accuracy']
            })
            
            # Update best parameters if better Sharpe ratio found
            if performance['sharpe_ratio'] > best_sharpe:
                best_sharpe = performance['sharpe_ratio']
                best_params = {
                    'short_window': short_window,
                    'long_window': long_window,
                    'ml_weight': ml_weight,
                    'performance': performance,
                    'train_metrics': train_metrics
                }
                
            print(f"Sharpe: {performance['sharpe_ratio']:.3f}, "
                  f"Return: {performance['total_return']:.2%}, "
                  f"Drawdown: {performance['max_drawdown']:.2%}")
            
        except Exception as e:
            print(f"Error with parameters {short_window}/{long_window}/{ml_weight}: {str(e)}")
            continue
    
    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv('optimization_results.csv', index=False)
    
    return best_params

def main():
    """Run parameter optimization"""
    # Load data
    df = pd.read_csv('../../data/MMM_data.csv', index_col='Date', parse_dates=True)
    
    # Run grid search
    best_params = grid_search_parameters(df)
    
    print("\nBest Parameters Found:")
    print(f"Short Window: {best_params['short_window']}")
    print(f"Long Window: {best_params['long_window']}")
    print(f"ML Weight: {best_params['ml_weight']}")
    print("\nPerformance:")
    print(f"Sharpe Ratio: {best_params['performance']['sharpe_ratio']:.3f}")
    print(f"Total Return: {best_params['performance']['total_return']:.2%}")
    print(f"Max Drawdown: {best_params['performance']['max_drawdown']:.2%}")
    print("\nML Metrics:")
    print(f"Train Accuracy: {best_params['train_metrics']['train_accuracy']:.2%}")
    print(f"Test Accuracy: {best_params['train_metrics']['test_accuracy']:.2%}")

if __name__ == "__main__":
    main()
