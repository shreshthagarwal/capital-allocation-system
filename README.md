# Nifty50 Hybrid Trading System

> A quantitative trading framework that combines mean reversion technical analysis with macro-economic sentiment scoring to generate data-driven intraday trading signals for the Indian equity market.

---

## 📖 Overview

The Nifty50 Hybrid Trading System is an algorithmic trading framework designed to address the limitations of traditional quantitative models that rely solely on historical price data. By integrating statistical analysis with real-time macro-economic intelligence, the system generates adaptive trading signals that account for both technical patterns and fundamental market context.

### Key Innovation

Traditional quantitative models often fail during:
- **Market regime transitions** (trending ↔ mean-reverting)
- **News-driven events** (policy changes, global shocks)
- **Structural market changes** (regulatory shifts, economic cycles)

This hybrid approach bridges the gap by:
1. **Statistical rigor** - Mean reversion analysis using Z-score methodology
2. **Contextual awareness** - Multi-factor macro sentiment scoring
3. **Dynamic allocation** - Confidence-weighted position sizing

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                     │
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │ Yahoo Finance   │  │ Manual Economic Indicators       │ │
│  │ - Nifty50 OHLCV │  │ - RBI Policy Rate               │ │
│  │ - S&P 500       │  │ - FII/DII Flow                  │ │
│  │ - USD-INR       │  │                                  │ │
│  │ - India VIX     │  │                                  │ │
│  └─────────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Analysis Modules                          │
│  ┌──────────────────┐  ┌──────────────────────────────────┐│
│  │  Module 1:       │  │  Module 2:                       ││
│  │  Technical       │  │  Macro Sentiment                 ││
│  │                  │  │                                  ││
│  │  • 20-day mean   │  │  • 5-factor scoring              ││
│  │  • Z-score calc  │  │  • Weighted aggregation          ││
│  │  • BUY/SELL/     │  │  • BULLISH/BEARISH/              ││
│  │    NEUTRAL       │  │    NEUTRAL                       ││
│  └──────────────────┘  └──────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Module 3: Decision Engine                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Signal Fusion Matrix                                  │ │
│  │  ─────────────────────────────────────────────────────│ │
│  │  Technical × Macro → Action + Allocation %            │ │
│  │                                                        │ │
│  │  • High Confidence: 80% allocation                    │ │
│  │  • Medium Confidence: 50% allocation                  │ │
│  │  • Low Confidence: 20% allocation                     │ │
│  │  • No Trade: 0% allocation                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Risk Management: 2% stop-loss | 1:2 risk-reward           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Output Layer                              │
│  • Trading signal (BUY/SELL/NO_TRADE)                       │
│  • Position size (% of capital)                             │
│  • Entry/Stop-loss/Target prices                            │
│  • Signal audit log (CSV)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔬 Methodology

### Module 1: Technical Analysis (Mean Reversion)

**Theoretical Foundation:** Mean reversion posits that asset prices exhibit a systematic tendency to revert toward their long-term equilibrium following periods of significant deviation (Poterba & Summers, 1988).

**Implementation:**
```
Z-score = (Current Price - Rolling Mean₂₀) / Rolling StdDev₂₀

Signal Logic:
  Z < -2.0  → BUY (Price oversold)
  Z > +2.0  → SELL (Price overbought)
  |Z| ≤ 2.0 → NEUTRAL (Price near equilibrium)
```

**Rationale:** The 20-day lookback period captures short-term price dislocations while remaining responsive to changing market dynamics. The 2-standard-deviation threshold provides a statistical basis for identifying extreme deviations with ~95% confidence under normal distribution assumptions.

---

### Module 2: Macro Sentiment Analysis

A rule-based framework that quantifies the directional impact of five key economic factors on equity market sentiment.

| Factor | Weight | Bullish Signal (+1) | Bearish Signal (-1) | Neutral (0) |
|--------|--------|---------------------|---------------------|-------------|
| **RBI Policy Rate** | 2× | Rate cut | Rate hike | No change |
| **FII Net Flow** | 2× | Inflow >1000cr | Outflow >1000cr | -1000 to +1000cr |
| **Global Indices** | 1× | S&P 500 up >0.5% | S&P 500 down >0.5% | -0.5% to +0.5% |
| **USD-INR** | 1× | Rupee strengthens | Rupee weakens | Stable |
| **India VIX** | 1× | VIX down >5% | VIX up >5% | -5% to +5% |

**Sentiment Score Calculation:**
```
Macro Score = Σ(Factor Signal × Weight)

Sentiment Classification:
  Score > +2  → BULLISH
  Score < -2  → BEARISH
  -2 ≤ Score ≤ +2 → NEUTRAL
```

**Economic Rationale:**
- **RBI Rate:** Direct impact on discount rates and liquidity conditions
- **FII Flow:** Foreign capital flows signal global risk appetite for emerging markets
- **Global Indices:** Correlation with Indian equities due to global risk-on/risk-off sentiment
- **USD-INR:** Currency strength affects export competitiveness and inflation
- **India VIX:** Volatility index reflects market fear and uncertainty

---

### Module 3: Dynamic Capital Allocation

The decision engine employs a confidence-weighted allocation framework that adjusts position sizes based on signal alignment.

**Decision Matrix:**

| Technical Signal | Macro Sentiment | Action | Capital Allocation | Confidence Level |
|------------------|-----------------|--------|-------------------|------------------|
| BUY | BULLISH | **BUY** | 80% | HIGH |
| BUY | NEUTRAL | **BUY** | 50% | MEDIUM |
| BUY | BEARISH | **BUY** | 20% | LOW |
| SELL | BEARISH | **SELL** | 80% | HIGH |
| SELL | NEUTRAL | **SELL** | 50% | MEDIUM |
| SELL | BULLISH | **SELL** | 20% | LOW |
| NEUTRAL | Any | **NO TRADE** | 0% | NONE |

**Risk Management Framework:**
- **Stop Loss:** 2% of allocated capital
- **Take Profit:** 4% of allocated capital (Risk:Reward = 1:2)
- **Intraday Square-off:** All positions closed by 3:15 PM IST
- **Maximum Allocation:** Capped at 80% of total capital

---

## 📊 Data Sources

### Automated Data Collection
- **Market Data:** Yahoo Finance API (`yfinance`)
  - Nifty50 Index (^NSEI)
  - S&P 500 Index (^GSPC)
  - USD-INR Exchange Rate (INR=X)
  - India VIX (^INDIAVIX)

### Manual Economic Indicators
- **RBI Policy Rate:** Reserve Bank of India official communications
  - Update Frequency: Bi-monthly (6 times per year)
  - Source: https://rbi.org.in/

- **FII/DII Flow:** National Stock Exchange daily reports
  - Update Frequency: Daily
  - Source: https://www.nseindia.com/market-data/investment-activity-fii-dii

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Internet connection (for data downloads)
- 50MB free disk space

### Quick Start

```bash
# 1. Clone/Download the project
git clone <repository-url>
cd capital-allocation-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run initial setup
python setup.py

# 4. Download historical data
python src/data_collection/fetch_nifty_data.py

# 5. Run the trading system
python main.py
```

### Configuration

Edit `config.yaml` to customize system parameters:

```yaml
trading:
  lookback_period: 20        # Days for mean calculation
  zscore_threshold: 2.0      # Signal trigger threshold
  capital_base: 100000       # Base capital in INR

allocation:
  high: 80      # High confidence allocation %
  medium: 50    # Medium confidence allocation %
  low: 20       # Low confidence allocation %

risk:
  stop_loss_pct: 2.0         # Stop loss percentage
  exit_time: "15:15"         # Intraday square-off time
```

---

## 💻 Usage

### Daily Analysis Workflow

**Quick Mode** (uses default macro values):
```bash
python main.py
```

**Manual Mode** (prompts for FII flow and RBI rate):
```bash
python main.py --manual
```

### Example Output

```
======================================================================
NIFTY50 HYBRID TRADING SYSTEM
Analysis Date: 2024-11-02 09:15:00
======================================================================

[MODULE 1: TECHNICAL ANALYSIS]
Signal: BUY
Z-Score: -2.3
Current Price: Rs.24,900 | Mean: Rs.25,580
Deviation: -2.66%

[MODULE 2: MACRO SENTIMENT]
Overall Sentiment: BULLISH
Score: +4
  • FII Flow: Strong inflow (+2)
  • Global Indices: Positive (+1)
  • India VIX: Falling (+1)

[MODULE 3: FINAL DECISION]
🎯 ACTION: BUY
💰 CAPITAL ALLOCATION: 80%
📊 CONFIDENCE: HIGH

Risk Management:
  Entry: Rs.24,900
  Stop Loss: Rs.24,402 (-2%)
  Target: Rs.25,398 (+2%)
  Capital Allocated: Rs.80,000
======================================================================
```

### Signal Log

All trading decisions are automatically logged to `data/signals/daily_signals.csv`:

| Date | Time | Action | Allocation | Confidence | Technical Signal | Macro Sentiment | Entry Price | Stop Loss | Target |
|------|------|--------|-----------|------------|-----------------|-----------------|-------------|-----------|--------|
| 2024-11-02 | 09:15 | BUY | 80% | HIGH | BUY | BULLISH | 24,900 | 24,402 | 25,398 |

---

## 📈 Performance Considerations

### When the System Generates Signals

**High Confidence Trades** (80% allocation):
- Strong technical extremes (Z-score beyond ±2.0)
- Aligned macro environment (Score beyond ±2)
- Clear directional conviction

**Medium/Low Confidence Trades** (50%/20% allocation):
- Moderate technical signals with neutral/conflicting macro
- Preservation of optionality with reduced exposure

**No Trade** (0% allocation):
- Technical neutrality (price near equilibrium)
- Absence of strong conviction from either module
- Capital preservation during uncertainty

### Risk Management Philosophy

The system prioritizes **capital preservation** over aggressive profit maximization:
- Conservative position sizing (maximum 80%)
- Strict stop-loss discipline (2% per trade)
- Intraday-only exposure (no overnight risk)
- Signal filtering to avoid low-probability setups

---

## 🛠️ Project Structure

```
capital-allocation-system/
├── config.yaml                    # System configuration
├── main.py                        # Main execution script
├── requirements.txt               # Python dependencies
├── README.md                      # This file
│
├── data/
│   ├── raw/                       # Downloaded market data
│   │   └── nifty50_daily.csv
│   ├── processed/                 # Processed datasets
│   └── signals/                   # Trading signal log
│       └── daily_signals.csv
│
├── src/
│   ├── data_collection/           # Data ingestion modules
│   │   └── fetch_nifty_data.py
│   ├── module1_technical/         # Technical analysis
│   │   └── mean_reversion.py
│   ├── module2_macro/             # Macro sentiment
│   │   └── macro_factors.py
│   └── module3_decision/          # Decision engine
│       └── capital_allocator.py
│
├── notebooks/                     # Jupyter analysis notebooks
│   └── 01_data_exploration.ipynb
│
└── results/                       # Analysis outputs
    └── visualizations/
```

---

## 📚 Theoretical Foundation

This system is grounded in established financial theories and empirical research:

### Mean Reversion
- **Poterba & Summers (1988):** Evidence of mean reversion in stock prices
- **Lo & MacKinlay (1988):** Variance ratio tests demonstrating return predictability

### Macro-Economic Factors
- **Chen, Roll & Ross (1986):** Macroeconomic variables and stock returns
- Monetary policy transmission mechanisms in emerging markets
- Capital flow dynamics and equity market performance

### Behavioral Finance
- Market overreaction hypothesis (De Bondt & Thaler, 1985)
- Sentiment-driven price deviations from fundamental values

---

## ⚠️ Limitations & Considerations

### Model Assumptions
- **Normal distribution:** Z-score methodology assumes normally distributed returns
- **Parameter stability:** 20-day lookback may not capture all regime changes
- **Linear relationships:** Factor weights are fixed and do not adapt dynamically

### Market Microstructure
- **Transaction costs:** Model does not account for market impact and slippage
- **Liquidity constraints:** Assumes execution at calculated prices
- **Regulatory factors:** Does not incorporate circuit breakers or trading halts

### Data Quality
- **Historical bias:** Backtested performance may not reflect future results
- **Survivorship bias:** Nifty50 composition changes over time
- **Look-ahead bias:** Mitigated through point-in-time data protocols

---

## 🎓 Academic Context

**Project Type:** Bachelor of Technology Mini Project  
**Domain:** Computer Science & Engineering
**Institution:** Bharati Vidyapeeth's College of Engineering  

**Authors:**
- Rishabh Goyal (04811502723)
- Shreshth Agarwal (04211502723)
- Pabitra Mondal (04711502723)

**Mentor:** Mr. Mohit Tiwari, Assistant Professor, Department of CSE

---

