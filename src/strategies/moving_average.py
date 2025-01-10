import pandas as pd
import numpy as np
from typing import Tuple, List
from numpy.typing import NDArray

class MovingAverageStrategy:
    """Moving Average Trading Strategy Implementation"""
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        """
        Initialize MA Strategy with window sizes
        
        Args:
            short_window (int): Short-term moving average window
            long_window (int): Long-term moving average window
        """
        self.short_window = short_window
        self.long_window = long_window
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals based on MA crossover
        
        Args:
            df (pd.DataFrame): DataFrame with 'Close' prices
            
        Returns:
            pd.DataFrame: DataFrame with signals
        """
        # Calculate moving averages
        df['SMA_short'] = df['Close'].rolling(window=self.short_window).mean()
        df['SMA_long'] = df['Close'].rolling(window=self.long_window).mean()
        
        # Generate signals
        df['Signal'] = 0
        df.loc[df['SMA_short'] > df['SMA_long'], 'Signal'] = 1  # Buy signal
        df.loc[df['SMA_short'] < df['SMA_long'], 'Signal'] = -1  # Sell signal
        
        # Calculate returns with transaction costs
        df['Returns'] = df['Close'].pct_change()
        
        # Add transaction costs (spread + commission)
        df['Signal_Change'] = df['Signal'].diff().abs()  # Detect trades
        df['Transaction_Costs'] = df['Signal_Change'] * 0.0015  # 15 bps per trade (10 bps spread + 5 bps commission)
        
        # Calculate strategy returns net of costs
        df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns'] - df['Transaction_Costs']
        
        return df
    
    def calculate_performance(self, df: pd.DataFrame) -> Tuple[float, float, float]:
        """
        Calculate strategy performance metrics
        
        Returns:
            Tuple[float, float, float]: (Sharpe ratio, Total return, Max drawdown)
        """
        returns = df['Strategy_Returns'].dropna()
        returns_array: NDArray[np.float64] = returns.to_numpy(dtype=np.float64)
        
        # Calculate Sharpe ratio (assuming risk-free rate = 0)
        annual_factor = np.sqrt(252)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        if std_return == 0:
            sharpe = 0.0
        else:
            sharpe = annual_factor * (mean_return / std_return)
        
        # Calculate total return
        cum_prod = np.prod(1.0 + returns_array)
        total_return = float(cum_prod) - 1.0
        
        # Calculate maximum drawdown
        cum_returns = np.cumprod(1.0 + returns_array)
        rolling_max = np.maximum.accumulate(cum_returns)
        drawdowns = cum_returns / rolling_max - 1.0
        max_drawdown = float(np.min(drawdowns))
        
        # Ensure all metrics are float values
        return float(sharpe), float(total_return), float(max_drawdown)
