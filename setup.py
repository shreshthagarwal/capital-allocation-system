"""
Setup Script for Nifty50 Hybrid Trading System
Run this once to set up the project structure and download initial data
"""

import os
import sys

def create_folder_structure():
    """Create all necessary folders"""
    print("Creating folder structure...")
    
    folders = [
        'data/raw',
        'data/processed',
        'data/signals',
        'src/data_collection',
        'src/module1_technical',
        'src/module2_macro',
        'src/module3_decision',
        'src/utils',
        'notebooks',
        'results',
        'results/visualizations',
        'docs',
        'tests'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        # Create __init__.py for Python packages
        if folder.startswith('src/'):
            init_file = os.path.join(folder, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'a').close()
    
    print("✓ Folder structure created")

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required = [
        'pandas',
        'numpy',
        'yfinance',
        'yaml',
        'matplotlib',
        'seaborn'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✓ All dependencies installed")
        return True

def check_config_file():
    """Check if config.yaml exists"""
    if not os.path.exists('config.yaml'):
        print("\n✗ config.yaml not found!")
        print("Please make sure config.yaml is in the root directory")
        return False
    return True

def download_initial_data():
    """Download initial Nifty50 data"""
    print("\nDownloading initial data...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from src.data_collection.fetch_nifty_data import download_nifty_data
        
        df = download_nifty_data()
        
        if df is not None:
            print(f"✓ Downloaded {len(df)} days of Nifty50 data")
            print(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")
            return True
        else:
            print("✗ Failed to download data")
            return False
    
    except Exception as e:
        print(f"✗ Error downloading data: {e}")
        print("This might be okay - you can download data later by running:")
        print("  python src/data_collection/fetch_nifty_data.py")
        return False

def create_sample_notebook():
    """Create a sample Jupyter notebook"""
    print("\nCreating sample notebook...")
    
    notebook_content = """{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Nifty50 Trading System - Data Exploration\\n",
    "\\n",
    "This notebook helps you explore and visualize the trading system data."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\\n",
    "import matplotlib.pyplot as plt\\n",
    "import sys\\n",
    "sys.path.append('../src')\\n",
    "\\n",
    "from src.data_collection.fetch_nifty_data import load_nifty_data\\n",
    "from src.module1_technical.mean_reversion import calculate_mean_reversion"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load data\\n",
    "df = load_nifty_data()\\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Calculate mean reversion indicators\\n",
    "df_processed = calculate_mean_reversion(df, lookback_period=20)\\n",
    "\\n",
    "# Plot price with rolling mean\\n",
    "plt.figure(figsize=(14, 6))\\n",
    "plt.plot(df_processed['Date'], df_processed['Close'], label='Close Price', linewidth=2)\\n",
    "plt.plot(df_processed['Date'], df_processed['rolling_mean'], label='20-day Mean', linestyle='--')\\n",
    "plt.xlabel('Date')\\n",
    "plt.ylabel('Price (INR)')\\n",
    "plt.title('Nifty50 Price with 20-Day Moving Average')\\n",
    "plt.legend()\\n",
    "plt.grid(True, alpha=0.3)\\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Plot Z-score\\n",
    "plt.figure(figsize=(14, 6))\\n",
    "plt.plot(df_processed['Date'], df_processed['zscore'], label='Z-Score', color='purple')\\n",
    "plt.axhline(y=2, color='r', linestyle='--', label='Overbought (+2)')\\n",
    "plt.axhline(y=-2, color='g', linestyle='--', label='Oversold (-2)')\\n",
    "plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)\\n",
    "plt.xlabel('Date')\\n",
    "plt.ylabel('Z-Score')\\n",
    "plt.title('Mean Reversion Z-Score')\\n",
    "plt.legend()\\n",
    "plt.grid(True, alpha=0.3)\\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}"""
    
    notebook_path = 'notebooks/01_data_exploration.ipynb'
    try:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            f.write(notebook_content)
        print(f"✓ Created {notebook_path}")
        return True
    except Exception as e:
        print(f"✗ Error creating notebook: {e}")
        return False

def run_setup():
    """Main setup function"""
    print("="*60)
    print("NIFTY50 HYBRID TRADING SYSTEM - SETUP")
    print("="*60)
    
    # Step 1: Create folders
    create_folder_structure()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n⚠ Please install missing dependencies first:")
        print("   pip install -r requirements.txt")
        return
    
    # Step 3: Check config file
    if not check_config_file():
        print("\n⚠ Please create config.yaml in the root directory")
        print("   You can copy it from the artifacts provided")
        return
    
    # Step 4: Download data
    download_initial_data()
    
    # Step 5: Create sample notebook
    create_sample_notebook()
    
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review config.yaml and adjust parameters if needed")
    print("2. Run the system: python main.py")
    print("3. For manual control: python main.py --manual")
    print("4. Explore data: jupyter notebook notebooks/01_data_exploration.ipynb")
    print("\nNote: No API keys needed - Yahoo Finance is free!")
    print("\n")

if __name__ == "__main__":
    run_setup()