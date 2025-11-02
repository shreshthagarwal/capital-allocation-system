"""
Capital Allocation Decision Engine
Combines technical signals with macro sentiment to make final trading decisions
"""

import yaml

def load_config():
    """Load configuration"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def make_trading_decision(technical_signal, macro_sentiment):
    """
    Combine technical and macro signals to generate final trading decision
    
    Parameters:
    -----------
    technical_signal : dict
        Output from Module 1 with keys: signal, zscore, current_price, etc.
    macro_sentiment : dict
        Output from Module 2 with keys: sentiment, score, breakdown
    
    Returns:
    --------
    dict
        Final decision with:
        - action: 'BUY', 'SELL', or 'NO_TRADE'
        - allocation_pct: Percentage of capital to allocate (0-80%)
        - confidence: 'HIGH', 'MEDIUM', 'LOW', or 'NONE'
        - reasoning: Explanation of the decision
        - technical_input: Echo of technical signal
        - macro_input: Echo of macro sentiment
        - risk_metrics: Stop loss and target calculations
    """
    
    config = load_config()
    
    tech_sig = technical_signal['signal']
    macro_sent = macro_sentiment['sentiment']
    
    # Decision matrix
    action = 'NO_TRADE'
    allocation_pct = 0
    confidence = 'NONE'
    reasoning = []
    
    # === BUY SCENARIOS ===
    if tech_sig == 'BUY':
        reasoning.append(f"Technical: Price oversold (Z-score: {technical_signal['zscore']})")
        
        if macro_sent == 'BULLISH':
            action = 'BUY'
            allocation_pct = config['allocation']['high']
            confidence = 'HIGH'
            reasoning.append(f"Macro: Strong bullish sentiment (Score: {macro_sentiment['score']})")
            reasoning.append("✓ Both signals aligned - HIGH confidence trade")
        
        elif macro_sent == 'NEUTRAL':
            action = 'BUY'
            allocation_pct = config['allocation']['medium']
            confidence = 'MEDIUM'
            reasoning.append(f"Macro: Neutral sentiment (Score: {macro_sentiment['score']})")
            reasoning.append("⚠ Mixed signals - MEDIUM confidence trade")
        
        elif macro_sent == 'BEARISH':
            action = 'BUY'
            allocation_pct = config['allocation']['low']
            confidence = 'LOW'
            reasoning.append(f"Macro: Bearish sentiment (Score: {macro_sentiment['score']})")
            reasoning.append("⚠ Conflicting signals - LOW confidence trade")
    
    # === SELL SCENARIOS ===
    elif tech_sig == 'SELL':
        reasoning.append(f"Technical: Price overbought (Z-score: {technical_signal['zscore']})")
        
        if macro_sent == 'BEARISH':
            action = 'SELL'
            allocation_pct = config['allocation']['high']
            confidence = 'HIGH'
            reasoning.append(f"Macro: Strong bearish sentiment (Score: {macro_sentiment['score']})")
            reasoning.append("✓ Both signals aligned - HIGH confidence trade")
        
        elif macro_sent == 'NEUTRAL':
            action = 'SELL'
            allocation_pct = config['allocation']['medium']
            confidence = 'MEDIUM'
            reasoning.append(f"Macro: Neutral sentiment (Score: {macro_sentiment['score']})")
            reasoning.append("⚠ Mixed signals - MEDIUM confidence trade")
        
        elif macro_sent == 'BULLISH':
            action = 'SELL'
            allocation_pct = config['allocation']['low']
            confidence = 'LOW'
            reasoning.append(f"Macro: Bullish sentiment (Score: {macro_sentiment['score']})")
            reasoning.append("⚠ Conflicting signals - LOW confidence trade")
    
    # === NEUTRAL TECHNICAL ===
    else:
        action = 'NO_TRADE'
        allocation_pct = 0
        confidence = 'NONE'
        reasoning.append("Technical: Price near equilibrium - no clear signal")
        reasoning.append("✗ No trade opportunity identified")
    
    # Calculate risk metrics
    risk_metrics = calculate_risk_metrics(
        action=action,
        current_price=technical_signal['current_price'],
        allocation_pct=allocation_pct,
        config=config
    )
    
    return {
        'action': action,
        'allocation_pct': allocation_pct,
        'confidence': confidence,
        'reasoning': '\n'.join(reasoning),
        'technical_input': technical_signal,
        'macro_input': macro_sentiment,
        'risk_metrics': risk_metrics
    }

def calculate_risk_metrics(action, current_price, allocation_pct, config):
    """
    Calculate stop loss and target prices
    
    Parameters:
    -----------
    action : str
        'BUY', 'SELL', or 'NO_TRADE'
    current_price : float
        Current market price
    allocation_pct : float
        Percentage of capital allocated
    config : dict
        Configuration dictionary
    
    Returns:
    --------
    dict
        Risk metrics including stop_loss, target, capital_at_risk
    """
    
    if action == 'NO_TRADE':
        return {
            'entry_price': None,
            'stop_loss': None,
            'target': None,
            'capital_allocated': 0,
            'capital_at_risk': 0
        }
    
    capital_base = config['trading']['capital_base']
    stop_loss_pct = config['risk']['stop_loss_pct']
    
    # Calculate allocated capital
    capital_allocated = (allocation_pct / 100) * capital_base
    
    # Calculate stop loss and target
    if action == 'BUY':
        stop_loss = current_price * (1 - stop_loss_pct / 100)
        target = current_price * (1 + stop_loss_pct / 100 * 2)  # 2:1 reward:risk
    else:  # SELL
        stop_loss = current_price * (1 + stop_loss_pct / 100)
        target = current_price * (1 - stop_loss_pct / 100 * 2)
    
    # Capital at risk
    capital_at_risk = capital_allocated * (stop_loss_pct / 100)
    
    return {
        'entry_price': round(current_price, 2),
        'stop_loss': round(stop_loss, 2),
        'target': round(target, 2),
        'capital_allocated': round(capital_allocated, 2),
        'capital_at_risk': round(capital_at_risk, 2),
        'risk_reward_ratio': '1:2'
    }

def print_decision_summary(decision):
    """Print formatted final decision"""
    print("\n" + "="*70)
    print("MODULE 3: FINAL TRADING DECISION")
    print("="*70)
    
    print(f"\n🎯 ACTION: {decision['action']}")
    print(f"💰 CAPITAL ALLOCATION: {decision['allocation_pct']}%")
    print(f"📊 CONFIDENCE: {decision['confidence']}")
    
    print("\n--- Decision Reasoning ---")
    print(decision['reasoning'])
    
    if decision['action'] != 'NO_TRADE':
        print("\n--- Risk Management ---")
        rm = decision['risk_metrics']
        print(f"Entry Price: ₹{rm['entry_price']}")
        print(f"Stop Loss: ₹{rm['stop_loss']}")
        print(f"Target: ₹{rm['target']}")
        print(f"Capital Allocated: ₹{rm['capital_allocated']:,.2f}")
        print(f"Capital at Risk: ₹{rm['capital_at_risk']:,.2f}")
        print(f"Risk:Reward Ratio: {rm['risk_reward_ratio']}")
    
    print("="*70)

def generate_trade_order(decision):
    """
    Generate executable trade order details
    
    Returns:
    --------
    dict or None
        Trade order details if action is BUY/SELL, None otherwise
    """
    
    if decision['action'] == 'NO_TRADE':
        return None
    
    config = load_config()
    rm = decision['risk_metrics']
    
    # Calculate quantity (assuming Nifty futures or simple shares)
    # For demo purposes, using lot size of 1
    quantity = int(rm['capital_allocated'] / rm['entry_price'])
    
    order = {
        'timestamp': None,  # To be filled at execution
        'symbol': 'NIFTY50',
        'action': decision['action'],
        'order_type': 'MARKET',  # Market order for intraday
        'quantity': quantity,
        'entry_price': rm['entry_price'],
        'stop_loss': rm['stop_loss'],
        'target': rm['target'],
        'exit_time': config['risk']['exit_time'],
        'confidence': decision['confidence'],
        'technical_zscore': decision['technical_input']['zscore'],
        'macro_score': decision['macro_input']['score']
    }
    
    return order

if __name__ == "__main__":
    # Test the decision engine
    print("=== Testing Decision Engine ===\n")
    
    # Mock inputs
    technical_signal = {
        'signal': 'BUY',
        'zscore': -2.3,
        'current_price': 24900,
        'mean_price': 25580,
        'deviation': -680,
        'deviation_pct': -2.66
    }
    
    macro_sentiment = {
        'sentiment': 'BULLISH',
        'score': 4,
        'breakdown': {}
    }
    
    # Make decision
    decision = make_trading_decision(technical_signal, macro_sentiment)
    
    # Print results
    print_decision_summary(decision)
    
    # Generate order
    order = generate_trade_order(decision)
    if order:
        print("\n--- Generated Trade Order ---")
        for key, value in order.items():
            print(f"{key}: {value}")