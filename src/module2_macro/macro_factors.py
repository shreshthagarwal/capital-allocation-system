"""
Macro Economic Factors Module
Rule-based analysis of 5 key macro indicators
"""

import yaml
import yfinance as yf
from datetime import datetime, timedelta

def load_config():
    """Load configuration"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

class MacroFactors:
    """
    Manages and evaluates 5 key macro-economic factors:
    1. RBI Policy Rate
    2. FII/DII Flow
    3. Global Indices (S&P 500)
    4. USD-INR Exchange Rate
    5. India VIX (Volatility Index)
    """
    
    def __init__(self):
        self.config = load_config()
        self.factors = {
            'rbi_rate': {'value': None, 'change': 0, 'weight': self.config['macro_weights']['rbi_rate']},
            'fii_flow': {'value': None, 'change': 0, 'weight': self.config['macro_weights']['fii_flow']},
            'global_indices': {'value': None, 'change': 0, 'weight': self.config['macro_weights']['global_indices']},
            'usd_inr': {'value': None, 'change': 0, 'weight': self.config['macro_weights']['usd_inr']},
            'india_vix': {'value': None, 'change': 0, 'weight': self.config['macro_weights']['india_vix']}
        }
    
    def set_rbi_rate(self, current_rate, previous_rate=None):
        """
        Set RBI policy rate
        
        Parameters:
        -----------
        current_rate : float
            Current repo rate (%)
        previous_rate : float, optional
            Previous repo rate for comparison
        
        Logic:
        ------
        Rate Cut (↓) = +1 (Bullish - easier money)
        Rate Hike (↑) = -1 (Bearish - tighter money)
        No Change = 0 (Neutral)
        """
        self.factors['rbi_rate']['value'] = current_rate
        
        if previous_rate is not None:
            if current_rate < previous_rate:
                self.factors['rbi_rate']['change'] = 1  # Rate cut = Bullish
            elif current_rate > previous_rate:
                self.factors['rbi_rate']['change'] = -1  # Rate hike = Bearish
            else:
                self.factors['rbi_rate']['change'] = 0  # No change
        else:
            # If no previous rate, assume neutral
            self.factors['rbi_rate']['change'] = 0
    
    def set_fii_flow(self, fii_net_flow_crores):
        """
        Set FII (Foreign Institutional Investor) net flow
        
        Parameters:
        -----------
        fii_net_flow_crores : float
            Net FII flow in crores (positive = inflow, negative = outflow)
        
        Logic:
        ------
        Strong Inflow (>1000 cr) = +1 (Bullish)
        Strong Outflow (<-1000 cr) = -1 (Bearish)
        Moderate flow = 0 (Neutral)
        """
        self.factors['fii_flow']['value'] = fii_net_flow_crores
        
        if fii_net_flow_crores > 1000:
            self.factors['fii_flow']['change'] = 1  # Strong inflow = Bullish
        elif fii_net_flow_crores < -1000:
            self.factors['fii_flow']['change'] = -1  # Strong outflow = Bearish
        else:
            self.factors['fii_flow']['change'] = 0  # Moderate flow = Neutral
    
    def fetch_global_indices(self):
        """
        Fetch S&P 500 performance (previous day)
        
        Logic:
        ------
        S&P up >0.5% = +1 (Bullish)
        S&P down >0.5% = -1 (Bearish)
        Otherwise = 0 (Neutral)
        """
        try:
            # Get S&P 500 last 2 days
            sp500 = yf.Ticker("^GSPC")
            hist = sp500.history(period="5d")
            
            if len(hist) >= 2:
                latest_close = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                
                pct_change = ((latest_close - previous_close) / previous_close) * 100
                
                self.factors['global_indices']['value'] = round(pct_change, 2)
                
                if pct_change > 0.5:
                    self.factors['global_indices']['change'] = 1  # Bullish
                elif pct_change < -0.5:
                    self.factors['global_indices']['change'] = -1  # Bearish
                else:
                    self.factors['global_indices']['change'] = 0  # Neutral
                
                return True
        except Exception as e:
            print(f"Warning: Could not fetch S&P 500 data: {e}")
            self.factors['global_indices']['change'] = 0
            return False
    
    def fetch_usd_inr(self):
        """
        Fetch USD-INR exchange rate trend
        
        Logic:
        ------
        Rupee strengthening (USD-INR down >0.3%) = +1 (Bullish)
        Rupee weakening (USD-INR up >0.3%) = -1 (Bearish)
        Otherwise = 0 (Neutral)
        """
        try:
            # Get USD-INR last 2 days
            usdinr = yf.Ticker("INR=X")
            hist = usdinr.history(period="5d")
            
            if len(hist) >= 2:
                latest_close = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                
                pct_change = ((latest_close - previous_close) / previous_close) * 100
                
                self.factors['usd_inr']['value'] = round(latest_close, 2)
                
                if pct_change < -0.3:
                    self.factors['usd_inr']['change'] = 1  # Rupee strengthening = Bullish
                elif pct_change > 0.3:
                    self.factors['usd_inr']['change'] = -1  # Rupee weakening = Bearish
                else:
                    self.factors['usd_inr']['change'] = 0  # Neutral
                
                return True
        except Exception as e:
            print(f"Warning: Could not fetch USD-INR data: {e}")
            self.factors['usd_inr']['change'] = 0
            return False
    
    def fetch_india_vix(self):
        """
        Fetch India VIX (Volatility Index)
        
        Logic:
        ------
        VIX falling (>5% drop) = +1 (Bullish - less fear)
        VIX rising (>5% rise) = -1 (Bearish - more fear)
        Otherwise = 0 (Neutral)
        """
        try:
            # Get India VIX last 2 days
            vix = yf.Ticker("^INDIAVIX")
            hist = vix.history(period="5d")
            
            if len(hist) >= 2:
                latest_close = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                
                pct_change = ((latest_close - previous_close) / previous_close) * 100
                
                self.factors['india_vix']['value'] = round(latest_close, 2)
                
                if pct_change < -5:
                    self.factors['india_vix']['change'] = 1  # VIX falling = Bullish
                elif pct_change > 5:
                    self.factors['india_vix']['change'] = -1  # VIX rising = Bearish
                else:
                    self.factors['india_vix']['change'] = 0  # Neutral
                
                return True
        except Exception as e:
            print(f"Warning: Could not fetch India VIX data: {e}")
            self.factors['india_vix']['change'] = 0
            return False
    
    def fetch_all_auto_factors(self):
        """Fetch all factors that can be automatically retrieved"""
        print("Fetching macro factors...")
        self.fetch_global_indices()
        self.fetch_usd_inr()
        self.fetch_india_vix()
        print("✓ Auto-fetch complete")
    
    def calculate_macro_score(self):
        """
        Calculate weighted macro sentiment score
        
        Returns:
        --------
        int
            Weighted sum of all factor changes
        """
        score = 0
        for factor_name, factor_data in self.factors.items():
            score += factor_data['change'] * factor_data['weight']
        return score
    
    def get_sentiment(self):
        """
        Get overall macro sentiment
        
        Returns:
        --------
        dict
            - sentiment: 'BULLISH', 'BEARISH', or 'NEUTRAL'
            - score: Weighted score
            - breakdown: Individual factor contributions
        """
        score = self.calculate_macro_score()
        
        bullish_threshold = self.config['macro_thresholds']['bullish']
        bearish_threshold = self.config['macro_thresholds']['bearish']
        
        if score > bullish_threshold:
            sentiment = 'BULLISH'
        elif score < bearish_threshold:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        # Create breakdown
        breakdown = {}
        for factor_name, factor_data in self.factors.items():
            breakdown[factor_name] = {
                'value': factor_data['value'],
                'signal': 'Positive' if factor_data['change'] == 1 else 'Negative' if factor_data['change'] == -1 else 'Neutral',
                'contribution': factor_data['change'] * factor_data['weight']
            }
        
        return {
            'sentiment': sentiment,
            'score': score,
            'breakdown': breakdown
        }

def print_macro_summary(sentiment_result):
    """Print formatted macro sentiment summary"""
    print("\n" + "="*60)
    print("MODULE 2: MACRO SENTIMENT ANALYSIS")
    print("="*60)
    
    print(f"\nOverall Sentiment: {sentiment_result['sentiment']}")
    print(f"Macro Score: {sentiment_result['score']}")
    
    print("\n--- Factor Breakdown ---")
    for factor, data in sentiment_result['breakdown'].items():
        print(f"{factor.upper()}:")
        print(f"  Value: {data['value']}")
        print(f"  Signal: {data['signal']}")
        print(f"  Contribution: {data['contribution']:+d}")
    
    print("="*60)

if __name__ == "__main__":
    # Test the module
    print("=== Testing Macro Factors Module ===\n")
    
    # Initialize
    macro = MacroFactors()
    
    # Set manual factors (RBI rate, FII flow)
    print("Setting manual factors...")
    macro.set_rbi_rate(current_rate=6.5, previous_rate=6.5)  # No change
    macro.set_fii_flow(fii_net_flow_crores=1500)  # Strong inflow
    
    # Fetch automatic factors
    macro.fetch_all_auto_factors()
    
    # Get sentiment
    sentiment = macro.get_sentiment()
    
    # Print results
    print_macro_summary(sentiment)