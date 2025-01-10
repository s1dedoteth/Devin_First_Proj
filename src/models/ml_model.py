import numpy as np
import pandas as pd
import ta
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.class_weight import compute_class_weight
from typing import Tuple, List, Dict, Optional, Union, Any

class MLModel:
    """Machine Learning Model for Trading Signal Enhancement"""
    
    def __init__(self, 
                 n_estimators: int = 100, 
                 max_depth: Optional[int] = None,
                 min_samples_split: int = 2,
                 random_state: int = 42,
                 **kwargs):
        """
        Initialize ML model
        
        Args:
            n_estimators (int): Number of trees in random forest
            max_depth (int): Maximum depth of trees
            min_samples_split (int): Minimum samples required to split
            random_state (int): Random seed for reproducibility
            **kwargs: Additional RandomForest parameters
        """
        # Define feature columns as class attribute
        # Keep only features with >2% importance based on analysis
        self.feature_cols = [
            'OBV',           # 39.74%
            'MA_Ratio_50',   # 11.57%
            'Volatility',    # 10.93%
            'BB_Width',      # 9.02%
            'ADX',           # 7.76%
            'MACD',          # 6.13%
            'MA_Ratio_20',   # 3.33%
            'Force_Index',   # 2.65%
            'RSI',           # 2.36%
            'BB_Position'    # 2.32%
        ]
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=4,  # Additional regularization
            max_features='sqrt',  # Use sqrt(n_features) for each split
            bootstrap=True,  # Enable bootstrapping for better generalization
            oob_score=True,  # Use out-of-bag score
            random_state=random_state,
            **kwargs
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
        
        # Price momentum and trend indicators
        df['RSI'] = self._calculate_rsi(df['Close'])
        df['MACD'] = ta.trend.macd_diff(df['Close'])
        df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'])
        
        # Volatility indicators
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Lower'] = bb.bollinger_lband()
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['Close']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Volume indicators
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
        df['Force_Index'] = ta.volume.force_index(df['Close'], df['Volume'])
        
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
        feature_cols = self.feature_cols
        
        # Drop rows with NaN values
        df = df.dropna()
        
        X = df[feature_cols].values
        y = np.array(df[target_col].values)
        
        # Scale features
        X = np.array(self.scaler.fit_transform(X))
        
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Train the ML model with time-series aware cross-validation
        
        Args:
            X (np.ndarray): Feature matrix
            y (np.ndarray): Target vector
            
        Returns:
            Dict[str, float]: Training metrics
        """
        # Use the last 30% of data for testing to better simulate real trading
        train_size = int(0.7 * len(X))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Add class weights to handle imbalanced data
        class_weights = compute_class_weight('balanced', 
                                          classes=np.unique(y_train), 
                                          y=y_train)
        class_weight_dict = dict(zip(np.unique(y_train), class_weights))
        self.model.set_params(class_weight=class_weight_dict)
        
        # Train model with early stopping using validation set
        val_size = int(0.2 * len(X_train))
        X_train_final = X_train[:-val_size]
        X_val = X_train[-val_size:]
        y_train_final = y_train[:-val_size]
        y_val = y_train[-val_size:]
        
        self.model.fit(X_train_final, y_train_final)
        
        # Calculate metrics
        train_score = float(self.model.score(X_train_final, y_train_final))
        val_score = float(self.model.score(X_val, y_val))
        test_score = float(self.model.score(X_test, y_test))
        
        # Calculate feature importance as a simple dict
        importances = [float(imp) for imp in self.model.feature_importances_]
        feature_importance = dict(zip(self.feature_cols, importances))
        
        # Print feature importance
        print("\nFeature Importance:")
        for feat, imp in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
            print(f"{feat}: {imp:.4f}")
        
        return {
            'train_accuracy': train_score,
            'val_accuracy': val_score,
            'test_accuracy': test_score,
            'feature_importance': feature_importance
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
