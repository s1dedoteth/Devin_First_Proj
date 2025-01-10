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
        
        # Train ML model with validation
        metrics = self.ml_model.train(X, y)
        
        print("\nTraining Metrics:")
        print(f"Train Accuracy: {metrics['train_accuracy']:.2%}")
        print(f"Validation Accuracy: {metrics['val_accuracy']:.2%}")
        print(f"Test Accuracy: {metrics['test_accuracy']:.2%}")
        
        # Convert numeric metrics to float, preserve feature importance dict
        return {
            'train_accuracy': float(metrics['train_accuracy']),
            'val_accuracy': float(metrics['val_accuracy']),
            'test_accuracy': float(metrics['test_accuracy']),
            'feature_importance': metrics['feature_importance']
        }
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals combining MA and ML
        
        Args:
            df (pd.DataFrame): Price data
            
        Returns:
            pd.DataFrame: DataFrame with combined signals
        """
        # Create features and get MA signals
        df = self.ml_model.create_features(df)
        df = self.ma_strategy.calculate_signals(df)
        
        # Get ML predictions
        X, _ = self.ml_model.prepare_data(df, target_col='Signal')
        ml_signals = self.ml_model.predict(X)
        
        # Set ML signals
        df['ML_Signal'] = 0
        signal_indices = df.index[-len(ml_signals):]
        df.loc[signal_indices, 'ML_Signal'] = ml_signals
        
        # Calculate initial signal (MA + ML weighted combination)
        raw_signal = (
            (1 - self.ml_weight) * df['Signal'] +
            self.ml_weight * df['ML_Signal']
        )
        df['Final_Signal'] = np.sign(raw_signal)
        
        # Calculate trend metrics
        trend_strength = df['MA_Ratio_50'].rolling(window=10).mean()
        trend_direction = np.sign(trend_strength - 1)
        trend_filter = (trend_direction * df['Final_Signal'] >= 0).astype(float)
        
        # Volatility-based position sizing
        vol_st = df['Returns'].rolling(window=10).std()
        vol_lt = df['Returns'].rolling(window=30).std()
        vol_position = (1 / (1 + 2 * vol_st)).clip(0.2, 1)  # Base position from volatility
        
        # Dynamic stop-loss
        stop_distance = (2 * vol_st).clip(0.02, 0.05)  # 2-5% stop loss
        trailing_stop = df['Close'].expanding().max() * (1 - stop_distance)
        stop_hit = (df['Close'] < trailing_stop).astype(float)
        
        # Calculate final position size combining all factors
        df['Position_Size'] = (
            vol_position *  # Base position from volatility
            trend_filter *  # Only take positions in trend direction
            (1 - stop_hit) *  # Exit when stop loss hit
            (0.5 + 0.5 * abs(trend_strength - 1).clip(0, 1))  # Scale with trend strength
        ).clip(0.2, 1)  # Minimum 20% position
        
        # Apply position sizing to final signal
        df['Final_Signal'] = df['Final_Signal'] * df['Position_Size']
        
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
        
        # Calculate returns with transaction costs
        df['Signal_Change'] = df['Final_Signal'].diff().abs()  # Detect trades
        df['Transaction_Costs'] = df['Signal_Change'] * 0.0015  # 15 bps per trade
        df['Strategy_Returns'] = df['Final_Signal'].shift(1) * df['Returns'] - df['Transaction_Costs']
        
        # Calculate performance metrics
        sharpe, total_return, max_drawdown = self.ma_strategy.calculate_performance(df)
        
        return {
            'sharpe_ratio': float(sharpe),
            'total_return': float(total_return),
            'max_drawdown': float(max_drawdown)
        }
