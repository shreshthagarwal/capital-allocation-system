"""
Nifty50 Hybrid Trading System - Main Execution Script

This script orchestrates all three modules:
1. Technical Analysis (Mean Reversion)
2. Macro Sentiment Analysis
3. Capital Allocation Decision

Run this script daily before market open to get trading signals.
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_collection.fetch_nifty_data import update_nifty_data
from src.module1_technical.mean_reversion import analyze_technical, print_technical_summary
from src.module2_macro.macro_factors import MacroFactors, print_macro_summary
from src.module3_decision.capital_allocator import make_trading_decision, print_decision_summary, generate_trade_order

def run_full_analysis(manual_rbi_rate=6.5, previous_rbi_rate=6.5, manual_fii_flow=0):
    """
    Execute complete trading system pipeline
    
    Parameters:
    -----------
    manual_rbi_rate : float
        Current RBI repo rate (%)
    previous_rbi_rate : float
        Previous RBI repo rate for comparison
    manual_fii_flow : float
        FII net flow in crores
    
    Returns:
    --------
    dict
        Complete analysis results
    """
    
    print("\n" + "="*70)
    print("NIFTY50 HYBRID TRADING SYSTEM")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # ========== STEP 1: UPDATE DATA ==========
    print("\n[STEP 1/4] Updating market data...")
    try:
        df = update_nifty_data()
        print("✓ Data updated successfully")
    except Exception as e:
        print(f"✗ Error updating data: {e}")
        return None
    
    # ========== STEP 2: TECHNICAL ANALYSIS ==========
    print("\n[STEP 2/4] Running technical analysis...")
    try:
        df_processed, technical_signal = analyze_technical(df)
        print_technical_summary(technical_signal)
    except Exception as e:
        print(f"✗ Error in technical analysis: {e}")
        return None
    
    # ========== STEP 3: MACRO SENTIMENT ANALYSIS ==========
    print("\n[STEP 3/4] Analyzing macro factors...")
    try:
        macro = MacroFactors()
        
        # Set manual factors
        macro.set_rbi_rate(current_rate=manual_rbi_rate, previous_rate=previous_rbi_rate)
        macro.set_fii_flow(fii_net_flow_crores=manual_fii_flow)
        
        # Fetch automatic factors
        macro.fetch_all_auto_factors()
        
        # Get sentiment
        macro_sentiment = macro.get_sentiment()
        print_macro_summary(macro_sentiment)
    except Exception as e:
        print(f"✗ Error in macro analysis: {e}")
        return None
    
    # ========== STEP 4: FINAL DECISION ==========
    print("\n[STEP 4/4] Making final trading decision...")
    try:
        decision = make_trading_decision(technical_signal, macro_sentiment)
        print_decision_summary(decision)
        
        # Generate trade order if applicable
        order = generate_trade_order(decision)
        
        if order:
            print("\n" + "="*70)
            print("📋 EXECUTABLE TRADE ORDER")
            print("="*70)
            print(f"Symbol: {order['symbol']}")
            print(f"Action: {order['action']}")
            print(f"Quantity: {order['quantity']}")
            print(f"Entry: ₹{order['entry_price']}")
            print(f"Stop Loss: ₹{order['stop_loss']}")
            print(f"Target: ₹{order['target']}")
            print(f"Exit Time: {order['exit_time']}")
            print("="*70)
        
        return {
            'timestamp': datetime.now(),
            'technical': technical_signal,
            'macro': macro_sentiment,
            'decision': decision,
            'order': order
        }
    
    except Exception as e:
        print(f"✗ Error in decision making: {e}")
        return None

def save_signal_to_file(results):
    """Save today's signal to CSV for record keeping"""
    import pandas as pd
    import os
    
    if results is None:
        return
    
    # Prepare data
    signal_data = {
        'date': results['timestamp'].strftime('%Y-%m-%d'),
        'time': results['timestamp'].strftime('%H:%M:%S'),
        'action': results['decision']['action'],
        'allocation_pct': results['decision']['allocation_pct'],
        'confidence': results['decision']['confidence'],
        'technical_signal': results['technical']['signal'],
        'technical_zscore': results['technical']['zscore'],
        'current_price': results['technical']['current_price'],
        'macro_sentiment': results['macro']['sentiment'],
        'macro_score': results['macro']['score'],
        'entry_price': results['decision']['risk_metrics']['entry_price'],
        'stop_loss': results['decision']['risk_metrics']['stop_loss'],
        'target': results['decision']['risk_metrics']['target']
    }
    
    # Create directory if not exists
    os.makedirs('data/signals', exist_ok=True)
    
    # Append to CSV
    filepath = 'data/signals/daily_signals.csv'
    df = pd.DataFrame([signal_data])
    
    if os.path.exists(filepath):
        df.to_csv(filepath, mode='a', header=False, index=False)
    else:
        df.to_csv(filepath, index=False)
    
    print(f"\n✓ Signal saved to {filepath}")

def quick_analysis():
    """
    Quick analysis mode - uses default macro values
    For daily quick checks
    """
    print("\n🚀 QUICK ANALYSIS MODE")
    print("Using default macro factor values")
    print("For manual control, use: python main.py --manual\n")
    
    results = run_full_analysis(
        manual_rbi_rate=6.5,
        previous_rbi_rate=6.5,
        manual_fii_flow=0
    )
    
    if results:
        save_signal_to_file(results)
    
    return results

def manual_analysis():
    """
    Manual analysis mode - prompts for macro inputs
    For detailed control over macro factors
    """
    print("\n📝 MANUAL ANALYSIS MODE")
    print("Please provide macro factor inputs:\n")
    
    try:
        current_rbi = float(input("Current RBI Repo Rate (%): "))
        previous_rbi = float(input("Previous RBI Repo Rate (%): "))
        fii_flow = float(input("FII Net Flow (Crores, + for inflow, - for outflow): "))
        
        results = run_full_analysis(
            manual_rbi_rate=current_rbi,
            previous_rbi_rate=previous_rbi,
            manual_fii_flow=fii_flow
        )
        
        if results:
            save_signal_to_file(results)
        
        return results
    
    except ValueError:
        print("✗ Invalid input. Please enter numeric values.")
        return None

if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        manual_analysis()
    else:
        quick_analysis()
    
    print("\n" + "="*70)
    print("Analysis complete. Trade safely! 📈")
    print("="*70 + "\n")