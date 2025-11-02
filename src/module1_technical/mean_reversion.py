"""
Mean Reversion Technical Analysis Module
Calculates Z-score and identifies overbought/oversold conditions
"""

import pandas as pd
import numpy as np
import yaml
import os
import sys

def load_config():
    """Load configuration from config.yaml"""
    
    # Try to find config.yaml
    config_path = 'config.yaml'
    
    # If running from src directory, go up two levels
    if not os.path.exists(config_path):
        config_path = '../../config.yaml'
    
    if not os.path.exists(config_path):
        # Create a default config if not found
        print("Warning: config.yaml not found. Using default values.")
        return {
            'trading': {
                'lookback_period': 20,
                'zscore_buy_threshold': -2.0,
                'zscore_sell_threshold': 2.0,
                'capital_base': 100000
            }
        }
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def calculate_mean_reversion(df, lookback_period=20):
    """
    Calculate mean reversion indicators
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with 'Close' column
    lookback_period : int
        Number of days for rolling mean calculation
    
    Returns:
    --------
    pandas.DataFrame
        Original dataframe with added columns:
        - rolling_mean: N-day moving average
        - rolling_std: N-day standard deviation
        - zscore: Z-score (standardized deviation from mean)
    """
    
    df = df.copy()
    
    # Calculate rolling mean and standard deviation
    df['rolling_mean'] = df['Close'].rolling(window=lookback_period).mean()
    df['rolling_std'] = df['Close'].rolling(window=lookback_period).std()
    
    # Calculate Z-score
    # Z-score = (Current Price - Mean) / Std Dev
    df['zscore'] = (df['Close'] - df['rolling_mean']) / df['rolling_std']
    
    # Calculate deviation in absolute terms
    df['deviation'] = df['Close'] - df['rolling_mean']
    df['deviation_pct'] = (df['deviation'] / df['rolling_mean']) * 100
    
    return df

def get_technical_signal(df, zscore_threshold=2.0):
    """
    Generate BUY/SELL/NEUTRAL signal based on Z-score
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with zscore column
    zscore_threshold : float
        Threshold for overbought/oversold (default: 2.0)
    
    Returns:
    --------
    dict
        Signal information with keys:
        - signal: 'BUY', 'SELL', or 'NEUTRAL'
        - zscore: Current Z-score value
        - current_price: Latest closing price
        - mean_price: Current rolling mean
        - deviation: Absolute deviation from mean
        - deviation_pct: Percentage deviation from mean
        - reason: Explanation of the signal
    """
    
    # Get latest row (most recent data)
    latest = df.iloc[-1]
    
    zscore = latest['zscore']
    current_price = latest['Close']
    mean_price = latest['rolling_mean']
    deviation = latest['deviation']
    deviation_pct = latest['deviation_pct']
    
    # Check if we have valid data
    if pd.isna(zscore):
        return {
            'signal': 'NO_DATA',
            'zscore': None,
            'current_price': current_price,
            'mean_price': None,
            'deviation': None,
            'deviation_pct': None,
            'reason': 'Insufficient data for calculation'
        }
    
    # Generate signal based on Z-score
    if zscore < -zscore_threshold:
        signal = 'BUY'
        reason = f'Price is oversold (Z-score: {zscore:.2f}). Price {abs(deviation_pct):.2f}% below mean.'
    elif zscore > zscore_threshold:
        signal = 'SELL'
        reason = f'Price is overbought (Z-score: {zscore:.2f}). Price {deviation_pct:.2f}% above mean.'
    else:
        signal = 'NEUTRAL'
        reason = f'Price is near equilibrium (Z-score: {zscore:.2f}).'
    
    return {
        'signal': signal,
        'zscore': round(zscore, 2),
        'current_price': round(current_price, 2),
        'mean_price': round(mean_price, 2),
        'deviation': round(deviation, 2),
        'deviation_pct': round(deviation_pct, 2),
        'reason': reason
    }

def analyze_technical(df=None):
    """
    Complete technical analysis pipeline
    
    Parameters:
    -----------
    df : pandas.DataFrame, optional
        If None, loads data from saved file
    
    Returns:
    --------
    tuple
        (processed_dataframe, signal_dict)
    """
    
    config = load_config()
    
    # Load data if not provided
    if df is None:
        # Add parent directory to path to import from src
        sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
        from src.data_collection.fetch_nifty_data import load_nifty_data
        df = load_nifty_data()
    
    # Calculate mean reversion indicators
    lookback = config['trading']['lookback_period']
    df_processed = calculate_mean_reversion(df, lookback_period=lookback)
    
    # Generate signal
    zscore_threshold = abs(config['trading']['zscore_buy_threshold'])
    signal = get_technical_signal(df_processed, zscore_threshold=zscore_threshold)
    
    return df_processed, signal

def print_technical_summary(signal):
    """
    Print formatted technical analysis summary
    """
    print("\n" + "="*60)
    print("MODULE 1: TECHNICAL ANALYSIS (Mean Reversion)")
    print("="*60)
    
    print(f"\nSignal: {signal['signal']}")
    print(f"Current Price: Rs.{signal['current_price']:,.2f}")
    print(f"Mean Price (20-day): Rs.{signal['mean_price']:,.2f}")
    print(f"Deviation: Rs.{signal['deviation']:,.2f} ({signal['deviation_pct']:.2f}%)")
    print(f"Z-Score: {signal['zscore']}")
    print(f"\nReason: {signal['reason']}")
    
    print("="*60)

if __name__ == "__main__":
    # Test the module
    print("=== Testing Mean Reversion Module ===\n")
    
    try:
        # Run analysis
        df_processed, signal = analyze_technical()
        
        # Print results
        print_technical_summary(signal)
        
        # Show last 10 rows with indicators
        print("\n=== Last 10 Days with Indicators ===")
        display_df = df_processed[['Date', 'Close', 'rolling_mean', 'zscore', 'deviation_pct']].tail(10).copy()
        
        # Format for better display
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
        display_df['Close'] = display_df['Close'].round(2)
        display_df['rolling_mean'] = display_df['rolling_mean'].round(2)
        display_df['zscore'] = display_df['zscore'].round(2)
        display_df['deviation_pct'] = display_df['deviation_pct'].round(2)
        
        print(display_df.to_string(index=False))
        
        print("\n=== Interpretation Guide ===")
        print("Z-Score < -2.0  → OVERSOLD (Strong BUY signal)")
        print("Z-Score > +2.0  → OVERBOUGHT (Strong SELL signal)")
        print("-2.0 < Z-Score < +2.0 → NEUTRAL (No clear signal)")
        
    except Exception as e:
        print(f"\n✗ Error running analysis: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure data is downloaded: python src/data_collection/fetch_nifty_data.py")
        print("2. Check that data/raw/nifty50_daily.csv exists")
        print("3. Verify config.yaml is in the root directory")