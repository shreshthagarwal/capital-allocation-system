"""
Fetch Nifty50 daily OHLCV data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
import yaml
from datetime import datetime, timedelta
import os

def load_config():
    """Load configuration from config.yaml"""
    import os
    
    # Try to find config.yaml
    config_path = 'config.yaml'
    
    # If running from src directory, go up two levels
    if not os.path.exists(config_path):
        config_path = '../../config.yaml'
    
    if not os.path.exists(config_path):
        # Create a default config if not found
        print("Warning: config.yaml not found. Using default values.")
        return {
            'data': {
                'nifty_symbol': '^NSEI',
                'start_date': '2022-01-01'
            },
            'paths': {
                'raw_data': 'data/raw/',
                'processed_data': 'data/processed/',
                'signals': 'data/signals/',
                'results': 'results/'
            }
        }
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def download_nifty_data(symbol=None, start_date=None, end_date=None, save=True):
    """
    Download Nifty50 historical data
    
    Parameters:
    -----------
    symbol : str, optional
        Yahoo Finance symbol (default from config)
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format
    end_date : str, optional
        End date in 'YYYY-MM-DD' format (default: today)
    save : bool
        Whether to save data to CSV
    
    Returns:
    --------
    pandas.DataFrame
        OHLCV data with columns: Date, Open, High, Low, Close, Volume
    """
    
    config = load_config()
    
    # Use config values if not provided
    if symbol is None:
        symbol = config['data']['nifty_symbol']
    if start_date is None:
        start_date = config['data']['start_date']
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Downloading {symbol} data from {start_date} to {end_date}...")
    
    try:
        # Download data from Yahoo Finance (auto_adjust=False to get all columns)
        df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=False)
        
        # Reset index to make Date a column
        df.reset_index(inplace=True)
        
        # Get actual column names (they might vary)
        print(f"Columns received: {list(df.columns)}")
        
        # Keep only the columns we need
        # Standard columns: Open, High, Low, Close, Adj Close, Volume
        columns_to_keep = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # Create new dataframe with only needed columns
        df_clean = pd.DataFrame()
        df_clean['Date'] = df['Date']
        df_clean['Open'] = df['Open']
        df_clean['High'] = df['High']
        df_clean['Low'] = df['Low']
        df_clean['Close'] = df['Close']
        df_clean['Volume'] = df['Volume']
        
        df = df_clean
        
        # Sort by date
        df.sort_values('Date', inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        print(f"✓ Downloaded {len(df)} rows")
        print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        
        # Save to CSV if requested
        if save:
            os.makedirs(config['paths']['raw_data'], exist_ok=True)
            filepath = os.path.join(config['paths']['raw_data'], 'nifty50_daily.csv')
            df.to_csv(filepath, index=False)
            print(f"✓ Saved to {filepath}")
        
        return df
    
    except Exception as e:
        print(f"✗ Error downloading data: {e}")
        return None

def load_nifty_data():
    """
    Load Nifty50 data from saved CSV file
    
    Returns:
    --------
    pandas.DataFrame
        OHLCV data
    """
    config = load_config()
    filepath = os.path.join(config['paths']['raw_data'], 'nifty50_daily.csv')
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        print("Downloading fresh data...")
        return download_nifty_data()
    
    df = pd.read_csv(filepath, parse_dates=['Date'])
    print(f"✓ Loaded {len(df)} rows from {filepath}")
    return df

def update_nifty_data():
    """
    Update existing data with latest prices
    Downloads only missing dates
    """
    config = load_config()
    filepath = os.path.join(config['paths']['raw_data'], 'nifty50_daily.csv')
    
    # Load existing data
    if os.path.exists(filepath):
        df_existing = pd.read_csv(filepath, parse_dates=['Date'])
        last_date = df_existing['Date'].max()
        
        # Download from last date + 1 day
        start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
        df_new = download_nifty_data(start_date=start_date, save=False)
        
        if df_new is not None and len(df_new) > 0:
            # Merge and save
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.drop_duplicates(subset=['Date'], keep='last', inplace=True)
            df_combined.sort_values('Date', inplace=True)
            df_combined.to_csv(filepath, index=False)
            print(f"✓ Added {len(df_new)} new rows")
            return df_combined
        else:
            print("✓ Data is already up to date")
            return df_existing
    else:
        # No existing data, download everything
        return download_nifty_data()

if __name__ == "__main__":
    # Test the functions
    print("=== Testing Nifty Data Downloader ===\n")
    
    # Download data
    df = download_nifty_data()
    
    # Display sample
    if df is not None:
        print("\n=== First 5 rows ===")
        print(df.head())
        
        print("\n=== Last 5 rows ===")
        print(df.tail())
        
        print("\n=== Data Info ===")
        print(df.info())