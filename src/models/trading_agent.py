import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from src.strategies.moving_average import MovingAverageStrategy
from src.models.ml_model import MLModel

class TradingAgent:
    """Trading Agent combining MA signals with ML predictions"""
    
    def __init__(self, 
                 short_window: int = 20,
                 long_window: int = 50,
                 ml_weight: float = 0.5,
                 ml_params: Optional[Dict] = None):
        """
        Initialize Trading Agent
        
        Args:
            short_window (int): Short-term MA window
            long_window (int): Long-term MA window
            ml_weight (float): Weight given to ML predictions (0-1)
            ml_params (Dict): ML model hyperparameters
        """
        self.ma_strategy = MovingAverageStrategy(short_window, long_window)
        self.ml_model = MLModel(**(ml_params or {}))
        self.ml_weight = ml_weight
        
    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Train the trading agent
        
        Args:
            df (pd.DataFrame): Historical price data
            
        Returns:
            Dict[str, float]: Training metrics
        """
        # Get MA signals
        df = self.ma_strategy.calculate_signals(df)
        
        # Create features and prepare data for ML
        df = self.ml_model.create_features(df)
        X, y = self.ml_model.prepare_data(df)
        
        # Train ML model
        metrics = self.ml_model.train(X, y)
        
        return metrics
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals combining MA and ML
        
        Args:
            df (pd.DataFrame): Price data
            
        Returns:
            pd.DataFrame: DataFrame with combined signals
        """
        # Get MA signals
        df = self.ma_strategy.calculate_signals(df)
        
        # Create features for ML
        df_features = self.ml_model.create_features(df)
        X, _ = self.ml_model.prepare_data(df_features, target_col='Signal')
        
        # Get ML predictions
        ml_signals = self.ml_model.predict(X)
        
        # Combine signals
        df['ML_Signal'] = 0
        signal_indices = df.index[-len(ml_signals):]
        df.loc[signal_indices, 'ML_Signal'] = ml_signals
        
        # Weighted combination of signals
        df['Final_Signal'] = (
            (1 - self.ml_weight) * df['Signal'] +
            self.ml_weight * df['ML_Signal']
        )
        
        # Convert to discrete signals (-1, 0, 1)
        df['Final_Signal'] = np.sign(df['Final_Signal'])
        
        return df
    
    def backtest(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Backtest the trading strategy
        
        Args:
            df (pd.DataFrame): Historical price data
            
        Returns:
            Dict[str, float]: Performance metrics
        """
        # Generate signals
        df = self.generate_signals(df)
        
        # Calculate returns
        df['Strategy_Returns'] = df['Final_Signal'].shift(1) * df['Returns']
        
        # Calculate performance metrics
        sharpe, total_return, max_drawdown = self.ma_strategy.calculate_performance(df)
        
        return {
            'sharpe_ratio': sharpe,
            'total_return': total_return,
            'max_drawdown': max_drawdown
        }
