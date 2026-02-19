# Statistical Arbitrage: Cointegration-Based Pairs Trading Strategy

## Overview

This project implements a fully modular **Statistical Arbitrage (Pairs Trading) pipeline in Python**.

The strategy identifies and trades **mean-reverting relationships between stocks** using:

- Cointegration testing (Engle-Granger method)  
- Stationarity testing (ADF test)  
- Hedge ratio estimation via OLS regression  
- Half-life filtering for mean reversion speed  
- Z-score based signal generation  
- Trade-level and portfolio-level backtesting  

The objective is to **systematically exploit temporary mispricing between statistically related assets**.

---

## Methodology

### 1. Data Collection

- Daily price data (~8+ years) downloaded using Yahoo Finance  
- Universe tested: **NIFTY 50 equities** (extendable to other universes)  
- Cleaned and aligned time series  
- Missing values removed for consistency  

---

### 2. Cointegration & Pair Selection

For every possible pair:

**Step 1: Estimate Hedge Ratio using OLS Regression**

\[
Y_t = \alpha + \beta X_t + \varepsilon_t
\]

**Step 2: Construct Spread**

\[
Spread_t = \log(Y_t) - \beta \log(X_t)
\]

**Step 3: Perform Stationarity Test**

- Augmented Dickey-Fuller (ADF) test applied to the spread  
- Pairs with **stationary spread (p-value < threshold)** are retained  

---

### 3. Half-Life Filtering

Mean reversion speed is estimated using **AR(1) regression**:

\[
\Delta S_t = \lambda S_{t-1} + \varepsilon_t
\]

Half-life is calculated as:

\[
Half\text{-}life = -\ln(2) / \lambda
\]

Only pairs with **sufficiently fast mean reversion** are selected.

---

### 4. Signal Generation

Spread is converted to a **rolling z-score**:

\[
Z_t = \frac{Spread_t - \mu_t}{\sigma_t}
\]

**Trading Rules:**

- Enter **LONG spread** when  
  \[
  Z < -\text{entry threshold}
  \]

- Enter **SHORT spread** when  
  \[
  Z > \text{entry threshold}
  \]

- Exit when  
  \[
  |Z| < \text{exit threshold}
  \]

- Stop-loss when divergence exceeds limit  

- Maximum holding period constraint enforced  

Signals are generated **pairwise and stored independently**.

---

### 5. Backtesting Engine

Each trade is constructed as:

- **Long Spread:**  
  \[
  (Y - \beta X)
  \]

- **Short Spread:**  
  \[
  (-Y + \beta X)
  \]

For each completed trade, the following are computed:

- Entry and exit values  
- Raw PnL  
- Return % normalized by entry cost  
- Holding period  
- Year-wise return aggregation  

**Performance Metrics:**

- Total Return  
- Average Return per Trade  
- Median Return  
- Win Rate  
- Average Holding Period  

---

### 6. Portfolio Construction

Pairs are filtered based on:

- Minimum total return threshold  
- Minimum win rate requirement  
- Minimum number of trades  
- Acceptable holding duration  

**Portfolio-level metrics computed:**

- Sharpe Ratio  
- Maximum Drawdown  
- Aggregate Return  

---

## Results

The strategy demonstrates:

- Robust mean-reversion behavior across selected pairs  
- Sharpe ratio approximately **3–4** (parameter dependent)  
- Consistent multi-year performance  
- High win rates (~55–75%)  

Performance sensitivity depends on:

- Entry and exit z-score thresholds  
- Stop-loss configuration  
- Maximum holding period limits  

---

## Key Features

- Fully modular pipeline  
- Robust statistical pair selection  
- Trade-level and portfolio-level evaluation  
- Extensible to any equity universe  
- Production-ready research framework  

---

## Applications

This framework can be extended for:

- Multi-asset statistical arbitrage  
- ETF pairs trading  
- Crypto statistical arbitrage  
- Market-neutral hedge fund strategies  
- Quantitative alpha research pipelines  

---

## Tech Stack

- Python  
- NumPy  
- Pandas  
- Statsmodels  
- SciPy  
- Matplotlib / Seaborn  

---

## Author

Siddhanth Gowda
