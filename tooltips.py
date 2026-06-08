TOOLTIPS = {

    "ema_fast": """
FAST EMA (Short-Term Trend)

What it does:
Tracks short-term price direction and reacts quickly to market changes.

Lower Values:
• Faster signals
• Earlier entries
• More false signals

Higher Values:
• Smoother trend detection
• Fewer false signals
• Later entries

Recommended:
• 20 = Balanced swing trading
• 10-15 = Aggressive trader
• 30-50 = Conservative trader

Default: 20
""",

    "ema_slow": """
SLOW EMA (Primary Trend Filter)

What it does:
Defines the dominant trend direction.

Price above Slow EMA:
• Bullish environment

Price below Slow EMA:
• Weak or bearish environment

Recommended:
• 50 = Swing trading
• 100 = Position trading
• 200 = Long-term investing

Default: 50
""",

    "breakout_len": """
BREAKOUT LOOKBACK PERIOD

What it does:
Determines how many previous bars are used to calculate resistance.

Lower Values:
• More breakout signals
• Earlier entries
• More false breakouts

Higher Values:
• Stronger breakout levels
• Fewer signals
• Higher quality setups

Recommended:
• 20 = Balanced
• 10-15 = Aggressive
• 40-80 = High conviction breakouts

Default: 20
""",

    "atr_len": """
ATR LOOKBACK PERIOD

What it does:
Measures market volatility.

Lower Values:
• ATR reacts faster
• Stops adjust quicker

Higher Values:
• Smoother volatility readings
• More stable stops

Recommended:
• 14 = Industry standard
• 7 = Aggressive
• 20-30 = Conservative

Default: 14
""",

    "atr_mult": """
INITIAL STOP LOSS DISTANCE

Formula:
Stop = Entry Price - (ATR × Multiplier)

Lower Values:
• Tighter stop
• Smaller losses
• Higher chance of stop-out

Higher Values:
• Wider stop
• Better trend survival
• Larger risk per trade

Recommended:
• 1.5 = Balanced
• 1.0 = Aggressive
• 2.0-3.0 = Volatile stocks

Default: 1.5
""",

    "trail_mult": """
TRAILING STOP DISTANCE

What it does:
Controls how tightly profits are protected.

Lower Values:
• Locks profits quickly
• Exits trends sooner

Higher Values:
• Gives trades more room
• Captures larger trends

Recommended:
• 1.2 = Balanced
• 1.0 = Aggressive
• 2.0+ = Trend following

Default: 1.2
""",

    "market_filter": """
SPY MARKET REGIME FILTER

What it does:
Uses SPY to determine whether overall market conditions are favorable.

Enabled:
• Bullish market = scanner operates normally
• Bearish market = setups are filtered

Disabled:
• Scanner ignores market direction

Recommended:
Enabled

Reason:
Most stocks follow the overall market trend.
Trading with the market typically improves win rates.
""",
}