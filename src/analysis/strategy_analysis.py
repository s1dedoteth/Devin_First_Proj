import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.models.trading_agent import TradingAgent

def analyze_signal_distribution(df: pd.DataFrame) -> Dict:
    """Analyze the distribution of trading signals"""
    signal_dist = {
        'MA_signals': df['Signal'].value_counts(normalize=True),
        'ML_signals': df['ML_Signal'].value_counts(normalize=True),
        'Final_signals': df['Final_Signal'].value_counts(normalize=True)
    }
    return signal_dist

def analyze_returns_by_regime(df: pd.DataFrame) -> Dict:
    """Analyze returns in different market regimes"""
    # Define market regimes based on volatility
    df = df.copy()
    df['Volatility'] = df['Returns'].rolling(window=20).std()
    df['Regime'] = pd.qcut(df['Volatility'].fillna(0), q=3, labels=['Low Vol', 'Med Vol', 'High Vol'])
    
    regime_performance = {}
    for regime in ['Low Vol', 'Med Vol', 'High Vol']:
        mask = df['Regime'] == regime
        returns_series = pd.Series(df.loc[mask, 'Strategy_Returns'].values).dropna()
        
        if len(returns_series) > 0:
            regime_performance[regime] = {
                'mean_return': float(returns_series.mean()),
                'sharpe': float(np.sqrt(252) * (returns_series.mean() / returns_series.std() if returns_series.std() != 0 else 1)),
                'win_rate': float((returns_series > 0).mean()),
                'num_trades': int(len(returns_series))
            }
    
    return regime_performance

def analyze_ml_predictions(df: pd.DataFrame) -> Dict:
    """Analyze ML model predictions vs actual returns"""
    # Compare ML signals with actual profitable trades
    df['Actual_Profitable'] = df['Returns'].shift(-1) > 0
    df['ML_Correct'] = (df['ML_Signal'] > 0) == df['Actual_Profitable']
    
    return {
        'accuracy': df['ML_Correct'].mean(),
        'precision': (df['ML_Signal'] > 0)[df['Actual_Profitable']].mean(),
        'recall': (df['Actual_Profitable'])[df['ML_Signal'] > 0].mean()
    }

def plot_performance_analysis(df: pd.DataFrame, save_path: str = 'analysis_plots.png'):
    """Create visualization of strategy analysis"""
    plt.figure(figsize=(15, 12))
    
    # Plot 1: Cumulative Returns by Regime
    plt.subplot(2, 2, 1)
    for regime in df['Regime'].unique():
        mask = df['Regime'] == regime
        cum_returns = (1 + df.loc[mask, 'Strategy_Returns']).cumprod()
        plt.plot(cum_returns.index, cum_returns, label=regime)
    plt.title('Cumulative Returns by Market Regime')
    plt.legend()
    
    # Plot 2: Signal Distribution
    plt.subplot(2, 2, 2)
    signals_df = pd.DataFrame({
        'MA': df['Signal'].value_counts(),
        'ML': df['ML_Signal'].value_counts(),
        'Final': df['Final_Signal'].value_counts()
    })
    signals_df.plot(kind='bar')
    plt.title('Signal Distribution')
    
    # Plot 3: Returns Distribution
    plt.subplot(2, 2, 3)
    sns.histplot(data=df['Strategy_Returns'].dropna(), bins=50)
    plt.title('Strategy Returns Distribution')
    
    # Plot 4: ML Prediction Accuracy Over Time
    plt.subplot(2, 2, 4)
    rolling_accuracy = df['ML_Correct'].rolling(window=50).mean()
    plt.plot(rolling_accuracy.index, rolling_accuracy)
    plt.title('ML Prediction Accuracy (50-day rolling)')
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def main():
    """Run strategy analysis"""
    # Load data
    df = pd.read_csv('data/MMM_data.csv', index_col='Date', parse_dates=True)
    
    # Initialize and run trading agent
    agent = TradingAgent(short_window=20, long_window=50, ml_weight=0.6)
    agent.train(df)
    df = agent.generate_signals(df)
    
    # Analyze strategy components
    signal_dist = analyze_signal_distribution(df)
    regime_perf = analyze_returns_by_regime(df)
    ml_metrics = analyze_ml_predictions(df)
    
    # Print analysis results
    print("\nSignal Distribution:")
    for signal_type, dist in signal_dist.items():
        print(f"\n{signal_type}:")
        print(dist)
    
    print("\nPerformance by Market Regime:")
    for regime, metrics in regime_perf.items():
        print(f"\n{regime}:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")
    
    print("\nML Model Analysis:")
    for metric, value in ml_metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # Create visualizations
    plot_performance_analysis(df)

if __name__ == "__main__":
    main()
