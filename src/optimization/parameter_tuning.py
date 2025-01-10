import pandas as pd
import numpy as np
from itertools import product
from typing import Dict, List, Tuple, Optional, Union, Any
from src.models.trading_agent import TradingAgent

# Configure pandas display options
pd.set_option('display.float_format', lambda x: '%.3f' % x)

def grid_search_parameters(
    df: pd.DataFrame,
    short_windows: List[int] = [5, 10, 15, 20, 25, 30],
    long_windows: List[int] = [20, 35, 50, 75, 100, 150, 200],
    ml_weights: List[float] = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
    max_depths: List[Optional[int]] = [3, 5, 8, 10, None],
    min_samples_splits: List[int] = [2, 5, 10],
    n_estimators_list: List[int] = [50, 100, 200]
) -> Dict[str, Any]:
    """
    Perform grid search over strategy parameters
    
    Args:
        df: Historical price data
        short_windows: List of short MA windows to test
        long_windows: List of long MA windows to test
        ml_weights: List of ML signal weights to test
        max_depths: List of max tree depths to test
        min_samples_splits: List of min samples split values
        n_estimators_list: List of number of trees to test
        
    Returns:
        Dict containing best parameters and their performance
    """
    best_sharpe = float('-inf')
    best_params = {}
    results = []
    
    # Generate valid parameter combinations
    valid_ma_pairs = [
        (short, long) 
        for short, long in product(short_windows, long_windows)
        if short < long  # Ensure short window is less than long window
    ]
    
    total_combinations = len(valid_ma_pairs) * len(ml_weights) * len(max_depths) * \
                        len(min_samples_splits) * len(n_estimators_list)
    print(f"\nTotal parameter combinations to test: {total_combinations}")
    current_combination = 0
    
    # Iterate through all combinations
    for short_window, long_window in valid_ma_pairs:
        for ml_weight in ml_weights:
            for max_depth in max_depths:
                for min_samples_split in min_samples_splits:
                    for n_estimators in n_estimators_list:
                        current_combination += 1
                        print(f"\nTesting combination {current_combination}/{total_combinations}")
                        print(f"Parameters: Short={short_window}, Long={long_window}, "
                              f"ML Weight={ml_weight}, Max Depth={max_depth}, "
                              f"Min Samples Split={min_samples_split}, "
                              f"N Estimators={n_estimators}")
                        
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
                            
                            # Create detailed results dictionary with explicit float conversion
                            result_dict = {
                                'short_window': short_window,
                                'long_window': long_window,
                                'ml_weight': ml_weight,
                                'max_depth': str(max_depth),  # Convert None to string for CSV
                                'min_samples_split': min_samples_split,
                                'n_estimators': n_estimators,
                                'sharpe_ratio': float(performance['sharpe_ratio']),
                                'total_return': float(performance['total_return']),
                                'max_drawdown': float(performance['max_drawdown']),
                                'train_accuracy': float(train_metrics['train_accuracy']),
                                'test_accuracy': float(train_metrics['test_accuracy'])
                            }
                            results.append(result_dict)
                            
                            # Save intermediate results every 10 combinations
                            if current_combination % 10 == 0:
                                pd.DataFrame(results).to_csv('optimization_results_interim.csv', index=False)
                            
                            # Update best parameters if better Sharpe ratio found
                            if performance['sharpe_ratio'] > best_sharpe:
                                best_sharpe = float(performance['sharpe_ratio'])
                                best_params = {
                                    'short_window': short_window,
                                    'long_window': long_window,
                                    'ml_weight': ml_weight,
                                    'max_depth': max_depth,
                                    'min_samples_split': min_samples_split,
                                    'n_estimators': n_estimators,
                                    'performance': performance,
                                    'train_metrics': train_metrics
                                }
                                print("\nNew best parameters found!")
                            
                            print(f"Sharpe: {performance['sharpe_ratio']:.3f}, "
                                  f"Return: {performance['total_return']:.2%}, "
                                  f"Drawdown: {performance['max_drawdown']:.2%}, "
                                  f"Train Acc: {train_metrics['train_accuracy']:.2%}, "
                                  f"Test Acc: {train_metrics['test_accuracy']:.2%}")
                            
                        except Exception as e:
                            print(f"Error with parameters: {str(e)}")
                            continue
            
            # Save intermediate results every 10 combinations
            if current_combination % 10 == 0:
                pd.DataFrame(results).to_csv('optimization_results_interim.csv', index=False)
            
            # Update best parameters if better Sharpe ratio found
            if performance['sharpe_ratio'] > best_sharpe:
                best_sharpe = performance['sharpe_ratio']
                best_params = {
                    'short_window': short_window,
                    'long_window': long_window,
                    'ml_weight': ml_weight,
                    'max_depth': max_depth,
                    'min_samples_split': min_samples_split,
                    'n_estimators': n_estimators,
                    'performance': performance,
                    'train_metrics': train_metrics
                }
                print("\nNew best parameters found!")
                
            print(f"Sharpe: {performance['sharpe_ratio']:.3f}, "
                  f"Return: {performance['total_return']:.2%}, "
                  f"Drawdown: {performance['max_drawdown']:.2%}, "
                  f"Train Acc: {train_metrics['train_accuracy']:.2%}, "
                  f"Test Acc: {train_metrics['test_accuracy']:.2%}")
            
        except Exception as e:
            print(f"Error with parameters: {str(e)}")
            continue
    
    # Save final results to CSV with proper formatting
    results_df = pd.DataFrame(results)
    
    # Sort results by Sharpe ratio for easier analysis
    results_df = results_df.sort_values('sharpe_ratio', ascending=False)
    
    # Format percentage columns
    for col in ['total_return', 'max_drawdown', 'train_accuracy', 'test_accuracy']:
        results_df[col] = results_df[col].map('{:.2%}'.format)
    
    # Save both full results and top 10
    results_df.to_csv('optimization_results.csv', index=False)
    results_df.head(10).to_csv('optimization_results_top10.csv', index=False)
    
    return best_params

def main():
    """Run parameter optimization"""
    try:
        # Load data
        df = pd.read_csv('data/MMM_data.csv', index_col='Date', parse_dates=True)
        
        # Run grid search
        best_params = grid_search_parameters(df)
        
        print("\nBest Parameters Found:")
        print(f"Short Window: {best_params['short_window']}")
        print(f"Long Window: {best_params['long_window']}")
        print(f"ML Weight: {best_params['ml_weight']}")
        print(f"Max Depth: {best_params['max_depth']}")
        print(f"Min Samples Split: {best_params['min_samples_split']}")
        print(f"N Estimators: {best_params['n_estimators']}")
        print("\nPerformance:")
        print(f"Sharpe Ratio: {best_params['performance']['sharpe_ratio']:.3f}")
        print(f"Total Return: {best_params['performance']['total_return']:.2%}")
        print(f"Max Drawdown: {best_params['performance']['max_drawdown']:.2%}")
        print("\nML Metrics:")
        print(f"Train Accuracy: {best_params['train_metrics']['train_accuracy']:.2%}")
        print(f"Test Accuracy: {best_params['train_metrics']['test_accuracy']:.2%}")
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
