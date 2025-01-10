import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from ..models import Stock, StockPrice, SuppressionScore

class SuppressionService:
    def __init__(self, db: Session):
        """Initialize suppression service with database session."""
        self.db = db
        # Default MA periods to analyze
        self.ma_periods = [5, 10, 20, 50, 100, 200]
        # Weights for suppression score calculation
        self.w1 = 0.5  # Contact rule weight
        self.w2 = 0.3  # Breakthrough rule weight
        self.w3 = 0.2  # Deviation rule weight
        # Default parameters
        self.contact_threshold = 0.02  # ±2% range for contact rule
        self.breakthrough_days = 5  # Days to check for fallback
        
    def calculate_moving_averages(self, prices: pd.DataFrame, period: int) -> pd.Series:
        """Calculate moving average for given period."""
        return prices['close'].rolling(window=period).mean()
    
    def detect_contacts(self, prices: pd.Series, ma: pd.Series, threshold: float) -> int:
        """
        Detect number of times price touches MA within threshold range.
        
        Args:
            prices: Series of closing prices
            ma: Series of moving average values
            threshold: Percentage threshold for contact detection
            
        Returns:
            Number of contacts detected
        """
        # Calculate percentage difference from MA
        diff_pct = abs(prices - ma) / ma
        # Count instances where price is within threshold of MA
        contacts = (diff_pct <= threshold).sum()
        return contacts
    
    def detect_breakthroughs(self, prices: pd.Series, ma: pd.Series, fallback_period: int) -> int:
        """
        Detect number of breakthrough and fallback patterns.
        
        Args:
            prices: Series of closing prices
            ma: Series of moving average values
            fallback_period: Number of days to check for fallback
            
        Returns:
            Number of breakthrough-fallback patterns
        """
        breakthroughs = 0
        # Create arrays for above/below MA
        above_ma = prices > ma
        
        for i in range(len(prices) - fallback_period):
            # Check for breakthrough (cross above MA)
            if not above_ma[i] and above_ma[i + 1]:
                # Check if price falls back below MA within fallback period
                if not above_ma[i + fallback_period:i + fallback_period + 1].any():
                    breakthroughs += 1
        
        return breakthroughs
    
    def calculate_average_deviation(self, prices: pd.Series, ma: pd.Series) -> float:
        """
        Calculate average deviation when price is below MA.
        
        Args:
            prices: Series of closing prices
            ma: Series of moving average values
            
        Returns:
            Average deviation as a percentage
        """
        try:
            # Convert to numpy arrays for calculation
            prices_arr = prices.to_numpy(dtype=np.float64)
            ma_arr = ma.to_numpy(dtype=np.float64)
            
            # Calculate deviation only when price is below MA
            below_ma = prices_arr < ma_arr
            if not np.any(below_ma):
                return 0.0
                
            # Calculate deviations as percentage
            deviations = np.where(below_ma, (ma_arr - prices_arr) / ma_arr * 100, 0)
            avg_deviation = np.mean(deviations[deviations != 0])
            
            return float(avg_deviation) if not np.isnan(avg_deviation) else 0.0
        except Exception as e:
            print(f"Error calculating average deviation: {e}")
            return 0.0
    
    def calculate_suppression_score(self, contacts: int, breakthroughs: int, 
                                  avg_deviation: float, total_days: int) -> float:
        """
        Calculate suppression score using weighted formula.
        
        Score = W1 * (C/T) + W2 * (B/T) - W3 * D
        where:
        - C: Number of contacts with MA
        - B: Number of breakthroughs and fallbacks
        - D: Average deviation from MA (%)
        - T: Total number of trading days
        """
        score = (
            self.w1 * (contacts / total_days) +
            self.w2 * (breakthroughs / total_days) -
            self.w3 * avg_deviation
        )
        return round(score, 4)
    
    def analyze_stock(self, stock: Stock, ma_period: int) -> Dict:
        """
        Analyze suppression patterns for a single stock and MA period.
        
        Returns:
            Dictionary containing suppression metrics and score
        """
        # Get price data
        prices = pd.DataFrame([
            {
                'date': price.date,
                'close': price.close
            }
            for price in stock.prices
        ]).set_index('date')
        
        if len(prices) < ma_period:
            return {
                'ma_period': ma_period,
                'score': 0.0,
                'contacts': 0,
                'breakthroughs': 0,
                'avg_deviation': 0.0
            }
            
        # Calculate MA
        ma = self.calculate_moving_averages(prices, ma_period)
        
        # Calculate metrics
        contacts = self.detect_contacts(
            prices['close'], 
            ma, 
            self.contact_threshold
        )
        
        breakthroughs = self.detect_breakthroughs(
            prices['close'], 
            ma, 
            self.breakthrough_days
        )
        
        avg_deviation = self.calculate_average_deviation(
            prices['close'], 
            ma
        )
        
        # Calculate final score
        score = self.calculate_suppression_score(
            contacts,
            breakthroughs,
            avg_deviation,
            len(prices)
        )
        
        return {
            'ma_period': ma_period,
            'score': score,
            'contacts': contacts,
            'breakthroughs': breakthroughs,
            'avg_deviation': avg_deviation
        }
    
    def analyze_all_stocks(self) -> None:
        """Analyze all stocks and store results in database."""
        stocks = self.db.query(Stock).all()
        
        for stock in stocks:
            # Clear existing scores
            self.db.query(SuppressionScore).filter(
                SuppressionScore.stock_id == stock.id
            ).delete()
            
            # Analyze each MA period
            for period in self.ma_periods:
                result = self.analyze_stock(stock, period)
                if result:
                    score = SuppressionScore(
                        stock_id=stock.id,
                        ma_period=period,
                        score=result['score'],
                        contacts=result['contacts'],
                        breakthroughs=result['breakthroughs'],
                        avg_deviation=result['avg_deviation']
                    )
                    self.db.add(score)
            
            try:
                self.db.commit()
                print(f"Successfully analyzed {stock.symbol}")
            except Exception as e:
                print(f"Error analyzing {stock.symbol}: {e}")
                self.db.rollback()
