Statistical Arbitrage: Cointegration-Based Pairs Trading Strategy
Overview

This project implements a fully modular Statistical Arbitrage (Pairs Trading) pipeline in Python.

The strategy identifies and trades mean-reverting relationships between stocks using:

• Cointegration testing (Engle-Granger method)
• Stationarity testing (ADF test)
• Hedge ratio estimation via OLS regression
• Half-life filtering for mean reversion speed
• Z-score based signal generation
• Trade-level and portfolio-level backtesting

The objective is to systematically exploit temporary mispricing between statistically related assets.

Methodology
1. Data Collection

Daily price data (~8+ years) downloaded using Yahoo Finance.

Universe tested:

NIFTY 50 equities (extendable to other universes)

Cleaned and aligned time series

Missing values removed for consistency

2. Cointegration & Pair Selection

For every possible pair:

Estimate hedge ratio using OLS regression:

Yₜ = α + βXₜ + εₜ

Construct spread:

Spreadₜ = log(Yₜ) − β log(Xₜ)

Perform Augmented Dickey-Fuller (ADF) test on spread.

Pairs with stationary spread (p-value < threshold) are retained.

3. Half-Life Filtering

Mean reversion speed estimated using AR(1) regression:

ΔSₜ = λ Sₜ₋₁ + εₜ

Half-life calculated as:

Half-life = −ln(2) / λ

Only pairs with sufficiently fast mean reversion are selected.

4. Signal Generation

Spread converted to rolling z-score:

Zₜ = (Spreadₜ − μₜ) / σₜ

Trading rules:

• Enter LONG when Z < −entry threshold
• Enter SHORT when Z > entry threshold
• Exit when |Z| < exit threshold
• Stop-loss when divergence increases
• Maximum holding period constraint

Signals are generated pairwise and stored separately.

5. Backtesting Engine

Each trade:

Long Spread → (Y − βX)
Short Spread → (−Y + βX)

For each completed trade:

Entry and exit values calculated

Raw PnL computed

Return % normalized by entry cost

Holding period measured

Year-wise returns aggregated

Performance metrics:

• Total Return
• Average Return per Trade
• Median Return
• Win Rate
• Average Holding Period

6. Portfolio Construction

Pairs filtered based on:

• Total return threshold
• Minimum win rate
• Sufficient number of trades
• Acceptable holding duration

Portfolio-level metrics computed:

• Sharpe Ratio
• Max Drawdown
• Aggregate Return

Results

The strategy demonstrates:

• Robust mean-reversion behavior across selected pairs
• Sharpe ratio approximately 3–4 (parameter dependent)
• Consistent multi-year performance
• High win rates (~55–75%)

Performance varies with:

Entry/Exit z-score thresholds

Stop-loss configuration


Holding period limits

