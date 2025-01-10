import pandas as pd
import numpy as np
from src.models.trading_agent import TradingAgent
import matplotlib.pyplot as plt
import seaborn as sns

def test_trading_agent():
    """Test the trading agent implementation"""
    # Load sample data (using MMM as test case)
    df = pd.read_csv('data/MMM_data.csv', index_col='Date', parse_dates=True)
    
    # Initialize trading agent
    agent = TradingAgent(short_window=20, long_window=50, ml_weight=0.6)
    
    # Train the agent
    print("Training trading agent...")
    metrics = agent.train(df)
    print("Training metrics:", metrics)
    
    # Generate signals and backtest
    print("\nRunning backtest...")
    performance = agent.backtest(df)
    print("Backtest performance:", performance)
    
    # Plot results
    df_signals = agent.generate_signals(df)
    plot_trading_signals(df_signals)
    
def plot_trading_signals(df: pd.DataFrame):
    """Create visualization of trading signals"""
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Price and Moving Averages
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df['Close'], label='Price', alpha=0.7)
    plt.plot(df.index, df['SMA_short'], label='Short MA', alpha=0.7)
    plt.plot(df.index, df['SMA_long'], label='Long MA', alpha=0.7)
    
    # Plot buy/sell signals
    buy_signals = df[df['Final_Signal'] == 1].index
    sell_signals = df[df['Final_Signal'] == -1].index
    
    plt.scatter(buy_signals, df.loc[buy_signals, 'Close'], 
               marker='^', color='g', label='Buy', alpha=0.7)
    plt.scatter(sell_signals, df.loc[sell_signals, 'Close'],
               marker='v', color='r', label='Sell', alpha=0.7)
    
    plt.title('Trading Signals')
    plt.legend()
    
    # Plot 2: Strategy Returns
    plt.subplot(2, 1, 2)
    cumulative_returns = (1 + df['Strategy_Returns']).cumprod()
    plt.plot(df.index, cumulative_returns, label='Strategy Returns')
    plt.title('Cumulative Strategy Returns')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('trading_signals.png')
    plt.close()

if __name__ == "__main__":
    test_trading_agent()
