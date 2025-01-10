import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from typing import Tuple, List, Dict

class MLModel:
    """Machine Learning Model for Trading Signal Enhancement"""
    
    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        """
        Initialize ML model
        
        Args:
            n_estimators (int): Number of trees in random forest
            random_state (int): Random seed for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state
        )
        self.scaler = StandardScaler()
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create technical features for ML model
        
        Args:
            df (pd.DataFrame): DataFrame with OHLCV data
            
        Returns:
            pd.DataFrame: DataFrame with technical features
        """
        df = df.copy()
        
        # Price-based features
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        # Volume features
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # Price momentum
        df['RSI'] = self._calculate_rsi(df['Close'])
        
        # Moving average features
        for window in [5, 10, 20, 50]:
            df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
            df[f'MA_Ratio_{window}'] = df['Close'] / df[f'MA_{window}']
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.astype(float).diff()
        gain = (delta.where(delta > 0, 0.0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.finfo(float).eps)  # Avoid division by zero
        return pd.Series(100 - (100 / (1 + rs)), index=prices.index)
    
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'Signal') -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for ML model
        
        Args:
            df (pd.DataFrame): DataFrame with features
            target_col (str): Name of target column
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: X (features) and y (target) arrays
        """
        feature_cols = [
            'Returns', 'Volatility', 'Volume_Ratio',
            'RSI', 'MA_Ratio_5', 'MA_Ratio_10',
            'MA_Ratio_20', 'MA_Ratio_50'
        ]
        
        # Drop rows with NaN values
        df = df.dropna()
        
        X = df[feature_cols].values
        y = np.array(df[target_col].values)
        
        # Scale features
        X = np.array(self.scaler.fit_transform(X))
        
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Train the ML model
        
        Args:
            X (np.ndarray): Feature matrix
            y (np.ndarray): Target vector
            
        Returns:
            Dict[str, float]: Training metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Calculate metrics
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X (np.ndarray): Feature matrix
            
        Returns:
            np.ndarray: Predicted trading signals
        """
        return self.model.predict(X)
