import os
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from dotenv import load_dotenv

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# ============================================================
# ENV
# ============================================================

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    st.error("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY")
    st.stop()

client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# ============================================================
# UI
# ============================================================

st.set_page_config(page_title="Swing Execution Engine v8", layout="wide")

st.title("📊 Swing Execution Engine v8")
st.caption("Clean breakout + execution system (NO RSI)")

# ============================================================
# DEFAULTS
# ============================================================

DEFAULTS = {
    "ema_fast": 20,
    "ema_slow": 50,
    "breakout_len": 20,
    "atr_len": 14,
    "atr_mult": 1.5,
}

# ============================================================
# RESET BUTTON (FIXED)
# ============================================================

if st.sidebar.button("🔄 Reset to Defaults"):
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()

# ============================================================
# SIDEBAR INPUTS (STATE SAFE)
# ============================================================

st.sidebar.header("⚙️ Settings")

EMA_FAST = st.sidebar.slider(
    "EMA Fast", 5, 50,
    st.session_state.get("ema_fast", DEFAULTS["ema_fast"]),
    key="ema_fast"
)

EMA_SLOW = st.sidebar.slider(
    "EMA Slow", 20, 200,
    st.session_state.get("ema_slow", DEFAULTS["ema_slow"]),
    key="ema_slow"
)

BREAKOUT_LEN = st.sidebar.slider(
    "Breakout Length", 5, 50,
    st.session_state.get("breakout_len", DEFAULTS["breakout_len"]),
    key="breakout_len"
)

ATR_LEN = st.sidebar.slider(
    "ATR Length", 5, 30,
    st.session_state.get("atr_len", DEFAULTS["atr_len"]),
    key="atr_len"
)

ATR_MULT = st.sidebar.slider(
    "ATR Multiplier", 1.0, 3.0,
    float(st.session_state.get("atr_mult", DEFAULTS["atr_mult"])),
    0.1,
    key="atr_mult"
)

# ============================================================
# WATCHLIST
# ============================================================

SYMBOLS = ["AAL", "SOFI", "MSFT", "NCLH", "HD", "META", "ORCL", "NKE"]

# ============================================================
# DATA
# ============================================================

def get_data(symbol, limit=400):
    req = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Hour,
        limit=limit
    )

    df = client.get_stock_bars(req).df.loc[symbol].copy()
    df = df.sort_index()

    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df.dropna()

# ============================================================
# INDICATORS
# ============================================================

def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def atr(df, length=14):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    atr_series = tr.ewm(alpha=1/length, adjust=False).mean()

    # safety fix (never None)
    atr_series = atr_series.ffill().bfill()

    return atr_series

def volume_ok(df):
    return df["volume"].iloc[-1] > df["volume"].rolling(20).mean().iloc[-1]

# ============================================================
# STATE
# ============================================================

def state(score):
    if score >= 4:
        return "🚀 BREAKOUT READY"
    elif score == 3:
        return "⚡ WATCH"
    elif score == 2:
        return "🔥 BUILDING"
    else:
        return "❌ NO TRADE"

# ============================================================
# ANALYSIS ENGINE (NO RSI)
# ============================================================

def analyze(df):
    close = df["close"]
    price = float(close.iloc[-1])

    ema_fast = ema(close, EMA_FAST)
    ema_slow = ema(close, EMA_SLOW)

    # -------------------------
    # TREND
    # -------------------------
    trend = price > ema_fast.iloc[-1] > ema_slow.iloc[-1]

    # -------------------------
    # MOMENTUM (price acceleration)
    # -------------------------
    momentum = ema_fast.iloc[-1] > ema_fast.iloc[-3] and price > ema_fast.iloc[-1]

    # -------------------------
    # BREAKOUT
    # -------------------------
    breakout = price > close.rolling(BREAKOUT_LEN).max().iloc[-2]

    # -------------------------
    # COMPRESSION
    # -------------------------
    compression = abs(price - ema_fast.iloc[-1]) / price < 0.015

    # -------------------------
    # VOLUME
    # -------------------------
    vol = volume_ok(df)

    # -------------------------
    # SCORE
    # -------------------------
    score = int(trend) + int(momentum) + int(breakout) + int(compression) + int(vol)

    # -------------------------
    # ATR EXECUTION
    # -------------------------
    atr_val = float(atr(df, ATR_LEN).iloc[-1])

    entry = price
    stop = price - ATR_MULT * atr_val
    risk = price - stop
    target = price + (2 * risk) if risk > 0 else price

    rr = (target - price) / risk if risk > 0 else 0

    # -------------------------
    # QUALITY
    # -------------------------
    if score == 5:
        quality = "🟢 A+ SETUP"
    elif score == 4:
        quality = "🟡 B SETUP"
    elif score == 3:
        quality = "🟠 C SETUP"
    else:
        quality = "🔴 NO TRADE"

    return {
        "Price": round(price, 2),
        "Score": score,
        "State": state(score),

        "Trend": "✅" if trend else "❌",
        "Compression": "✅" if compression else "❌",
        "Volume": "✅" if vol else "❌",
        "Momentum": "📈" if momentum else "📉",
        "Breakout": "✅" if breakout else "❌",

        "Entry": round(entry, 2),
        "Stop": round(stop, 2),
        "Target": round(target, 2),
        "R/R": round(rr, 2),

        "Quality": quality
    }

# ============================================================
# MARKET FILTER
# ============================================================

def market_status():
    try:
        spy = get_data("SPY")
        close = spy["close"]
        ema50 = ema(close, 50)

        bullish = close.iloc[-1] > ema50.iloc[-1]
        return ("🟢 BULLISH" if bullish else "🔴 BEARISH", bullish)
    except:
        return ("⚪ UNKNOWN", False)

# ============================================================
# RUN SCAN
# ============================================================

market_text, _ = market_status()

c1, c2 = st.columns([4, 1])

with c1:
    st.success(f"Market: {market_text}")

with c2:
    st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

results = []

for s in SYMBOLS:
    try:
        df = get_data(s)
        row = analyze(df)
        row["Symbol"] = s
        results.append(row)
    except:
        results.append({
            "Symbol": s,
            "Price": 0,
            "Score": 0,
            "State": "ERROR",
            "Momentum": "❌",
            "Trend": "❌",
            "Breakout": "❌",
            "Compression": "❌",
            "Volume": "❌",
            "Entry": 0,
            "Stop": 0,
            "Target": 0,
            "R/R": 0,
            "Quality": "❌"
        })

df = pd.DataFrame(results).sort_values("Score", ascending=False)

# ============================================================
# TOP PICK
# ============================================================

top = df.iloc[0]

st.subheader("🥇 Best Setup")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Symbol", top["Symbol"])
c2.metric("Price", f"{top['Price']:.2f}")
c3.metric("Score", int(top["Score"]))
c4.metric("R/R", f"{top['R/R']:.2f}")

st.markdown(f"### {top['Quality']}")

# ============================================================
# TABLE
# ============================================================

st.subheader("📊 Execution Dashboard")

st.dataframe(
    df[[
        "Symbol",
        "Price",
        "Score",
        "Quality",
        "Trend",
        "Compression",
        "Volume",
        "Momentum",
        "Breakout",
        "Entry",
        "Stop",
        "Target",
        "R/R"
    ]].style.format({
        "Price": "{:.2f}",
        "Entry": "{:.2f}",
        "Stop": "{:.2f}",
        "Target": "{:.2f}",
        "R/R": "{:.2f}",
    }),
    use_container_width=True
)

# ============================================================
# GUIDE
# ============================================================

with st.expander("How to Use"):
    st.markdown("""
### Setup Types
- 🟢 A+ = Best breakout setup
- 🟡 B = Good setup
- 🟠 C = Weak setup
- 🔴 Ignore

### Execution
- Entry = current price
- Stop = ATR-based risk
- Target = 2R reward

### Logic
- Trend alignment
- Momentum acceleration
- Breakout confirmation
- Compression before move
- Volume confirmation
""")