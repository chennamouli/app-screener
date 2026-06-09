# PRO QUANT EXECUTION ENGINE v9

## User Guide & Technical Documentation

---

# Overview

PRO QUANT v9 is a swing trading scanner designed to identify stocks with:

* Strong trend
* Positive momentum
* Breakout potential
* Healthy volume
* Favorable market conditions

The scanner operates on **1-Hour charts** and optionally uses **SPY market regime** as a global filter.

---

# Scanner Workflow

The scanner evaluates each stock using the following sequence:

Trend → Compression → Volume → Momentum → Breakout → Score → Trade Plan

Each condition contributes to the overall score.

Higher scores indicate stronger setups.

---

# Settings (Tuners)

## EMA Fast

Purpose:
Short-term trend measurement.

Calculation:
Exponential Moving Average of closing prices.

Impact:

* Lower value = faster response, more signals
* Higher value = smoother response, fewer signals

Recommended:
20

Default:
20

---

## EMA Slow

Purpose:
Primary trend filter.

Calculation:
Longer-term Exponential Moving Average.

Impact:

* Lower value = more responsive
* Higher value = more stable trend detection

Recommended:
50

Default:
50

---

## Breakout Length

Purpose:
Determines resistance level used for breakout detection.

Calculation:
Highest closing price over previous N bars.

Impact:

* Lower value = more breakout signals
* Higher value = stronger breakout confirmation

Recommended:
20

Default:
20

---

## ATR Length

Purpose:
Volatility measurement.

Calculation:
Average True Range over N bars.

Impact:

* Lower value = faster adaptation
* Higher value = smoother volatility estimate

Recommended:
14

Default:
14

---

## ATR Multiplier

Purpose:
Initial stop-loss distance.

Calculation:

Stop = Entry − (ATR × Multiplier)

Impact:

* Lower value = tighter stop
* Higher value = wider stop

Recommended:
1.5

Default:
1.5

---

## Trailing Stop Multiplier

Purpose:
Profit protection.

Calculation:

Trailing Stop = Price − (ATR × Multiplier)

Impact:

* Lower value = tighter trailing stop
* Higher value = allows larger trends

Recommended:
1.2

Default:
1.2

---

## Market Regime Filter (SPY)

Purpose:
Filters trades based on overall market direction.

Calculation:

SPY Close > SPY EMA50

Result:

* Enabled = market direction influences score
* Disabled = scanner ignores market direction

Recommended:
Enabled

Default:
Disabled

---

# Market Regime Logic

Bullish Market:

SPY Close > SPY EMA50

Bearish Market:

SPY Close ≤ SPY EMA50

Banner Values:

🟢 BULLISH

🔴 BEARISH

---

# Signal Calculations

## Trend

Purpose:
Determine if the stock is in a strong uptrend.

Calculation:

Price > EMA Fast > EMA Slow

Values:

✅ = Trend confirmed

❌ = Trend not confirmed

---

## Momentum

Purpose:
Measure trend acceleration.

Calculation:

EMA Fast(Current) > EMA Fast(3 bars ago)

Values:

📈 = Momentum rising

❌ = Momentum weakening

---

## Compression

Purpose:
Identify stocks consolidating near trend support.

Calculation:

|Price − EMA Fast| ÷ Price < 1.5%

Values:

✅ = Tight consolidation

❌ = Extended from trend

---

## Volume

Purpose:
Confirm institutional participation.

Calculation:

Current Volume > 20-Bar Average Volume

Values:

✅ = Above average volume

❌ = Below average volume

---

## Breakout

Purpose:
Detect new highs above recent resistance.

Calculation:

Current Close >
Highest Close of previous Breakout Length bars

Values:

✅ = Breakout detected

❌ = No breakout

---

# Score Calculation

Maximum Score = 6

Components:

1 Point → Trend

1 Point → Momentum

1 Point → Compression

1 Point → Volume

1 Point → Breakout

1 Point → Market Regime (if enabled)

Formula:

Score =
Trend +
Momentum +
Compression +
Volume +
Breakout +
Regime

Range:

0 → 6

---

# Setup Quality

## A+ Setup

Score ≥ 6

Meaning:
All major conditions aligned.

Display:

🟢 A+ SETUP

---

## B Setup

Score = 5

Meaning:
Strong setup with one missing component.

Display:

🟡 B SETUP

---

## C Setup

Score = 4

Meaning:
Developing setup.

Display:

🟠 C SETUP

---

## No Trade

Score ≤ 3

Meaning:
Insufficient confirmation.

Display:

🔴 NO TRADE

---

# Dashboard Columns

## Symbol

Stock ticker.

Examples:

AAPL

MSFT

META

---

## Price

Current stock price.

Example:

245.37

---

## Score

Total scanner score.

Range:

0 – 6

Higher is better.

---

## Quality

Overall setup grade.

Values:

🟢 A+ SETUP

🟡 B SETUP

🟠 C SETUP

🔴 NO TRADE

---

## Trend

Trend confirmation.

Values:

✅

❌

---

## Compression

Consolidation status.

Values:

✅

❌

---

## Volume

Volume confirmation.

Values:

✅

❌

---

## Momentum

Momentum direction.

Values:

📈

❌

---

## Breakout

Breakout confirmation.

Values:

✅

❌

---

## Entry

Current price used as entry reference.

Example:

245.37

---

## Stop

ATR-based protective stop.

Example:

239.10

---

## Target

2R profit target.

Formula:

Target = Entry + (2 × Risk)

Example:

257.91

---

## R/R

Risk-to-Reward ratio.

Formula:

(Target − Entry) ÷ (Entry − Stop)

Typical Values:

1.0

1.5

2.0

Current Engine Target:

2.0

---

# Recommended Settings

For most swing traders:

EMA Fast = 20

EMA Slow = 50

Breakout Length = 20

ATR Length = 14

ATR Multiplier = 1.5

Trailing Stop Multiplier = 1.2

Market Filter = Enabled

These settings are optimized for 1-Hour swing trading.
