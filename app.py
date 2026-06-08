import os
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import pytz

from dotenv import load_dotenv

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from tooltips import TOOLTIPS

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

st.set_page_config(page_title="PRO QUANT v9", layout="wide")

st.title("📊 PRO QUANT EXECUTION ENGINE v9")
st.caption("Clean swing system: 1H + SPY regime + breakout engine")

# ============================================================
# DEFAULTS
# ============================================================

DEFAULTS = {
    "ema_fast": 20,
    "ema_slow": 50,
    "breakout_len": 20,
    "atr_len": 14,
    "atr_mult": 1.5,
    "trail_mult": 1.2,
    "use_market_filter": False,
}

# ============================================================
# RESET BUTTON (RESTORED)
# ============================================================

if st.sidebar.button("🔄 Reset to Defaults"):
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Settings")

EMA_FAST = st.sidebar.slider("EMA Fast", 5, 50, st.session_state.get("ema_fast", DEFAULTS["ema_fast"]), key="ema_fast", help=TOOLTIPS.get("ema_fast"))
EMA_SLOW = st.sidebar.slider("EMA Slow", 20, 200, st.session_state.get("ema_slow", DEFAULTS["ema_slow"]), key="ema_slow", help=TOOLTIPS.get("ema_slow"))

BREAKOUT_LEN = st.sidebar.slider("Breakout Length", 10, 80, st.session_state.get("breakout_len", DEFAULTS["breakout_len"]), key="breakout_len", help=TOOLTIPS.get("breakout_len"))
ATR_LEN = st.sidebar.slider("ATR Length", 5, 30, st.session_state.get("atr_len", DEFAULTS["atr_len"]), key="atr_len", help=TOOLTIPS.get("atr_len"))

ATR_MULT = st.sidebar.slider("ATR Multiplier", 1.0, 3.0, st.session_state.get("atr_mult", DEFAULTS["atr_mult"]), 0.1, key="atr_mult", help=TOOLTIPS.get("atr_mult"))

TRAIL_MULT = st.sidebar.slider("Trailing Stop Multiplier", 0.8, 3.0, st.session_state.get("trail_mult", DEFAULTS["trail_mult"]), 0.1, key="trail_mult", help=TOOLTIPS.get("trail_mult"))

USE_MARKET_FILTER = st.sidebar.checkbox(
    "📊 Market Regime Filter (SPY)",
    value=st.session_state.get("use_market_filter", False),
    key="use_market_filter", help=TOOLTIPS.get("market_filter")
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

    return tr.ewm(alpha=1/length, adjust=False).mean().ffill().bfill()

# ============================================================
# CLEAN BREAKOUT (FIXED)
# ============================================================

def breakout(df):
    close = df["close"]
    level = close.rolling(BREAKOUT_LEN).max().iloc[-2]
    return close.iloc[-1] > level

# ============================================================
# VOLUME FILTER (CLEAN)
# ============================================================

def volume_ok(df):
    vol = df["volume"]
    avg = vol.rolling(20).mean()
    return not avg.isna().iloc[-1] and vol.iloc[-1] > avg.iloc[-1]

# ============================================================
# MARKET REGIME (GLOBAL ONLY)
# ============================================================

def compute_spy_regime():
    spy = get_data("SPY")
    close = spy["close"]
    ema50 = ema(close, 50)
    return close.iloc[-1] > ema50.iloc[-1]

SPY_REGIME = compute_spy_regime()

# ============================================================
# ANALYSIS ENGINE
# ============================================================

def analyze(df):
    close = df["close"]
    price = float(close.iloc[-1])

    ema_fast = ema(close, EMA_FAST)
    ema_slow = ema(close, EMA_SLOW)

    # TREND
    trend = price > ema_fast.iloc[-1] > ema_slow.iloc[-1]

    # MOMENTUM (slope proxy)
    momentum = ema_fast.iloc[-1] > ema_fast.iloc[-3]

    # BREAKOUT
    brk = breakout(df)

    # COMPRESSION
    compression = abs(price - ema_fast.iloc[-1]) / price < 0.015

    # VOLUME
    vol = volume_ok(df)

    # REGIME FILTER
    regime_ok = SPY_REGIME if USE_MARKET_FILTER else True

    # SCORE (CLEAN + BALANCED)
    score = (
        int(trend)
        + int(momentum)
        + int(brk)
        + int(compression)
        + int(vol)
        + int(regime_ok)
    )

    # ATR STOP SYSTEM
    atr_val = float(atr(df, ATR_LEN).iloc[-1])

    entry = price
    stop = price - ATR_MULT * atr_val
    trail = price - TRAIL_MULT * atr_val
    stop = min(stop, trail)

    risk = price - stop
    target = price + 2 * risk if risk > 0 else price
    rr = (target - price) / risk if risk > 0 else 0

    # QUALITY
    if score >= 6:
        quality = "🟢 A+ SETUP"
    elif score == 5:
        quality = "🟡 B SETUP"
    elif score == 4:
        quality = "🟠 C SETUP"
    else:
        quality = "🔴 NO TRADE"

    return {
        "Symbol": df.attrs["symbol"],
        "Price": round(price, 2),
        "Score": score,
        "Quality": quality,

        "Trend": "✅" if trend else "❌",
        "Compression": "✅" if compression else "❌",
        "Volume": "✅" if vol else "❌",
        "Momentum": "📈" if momentum else "❌",
        "Breakout": "✅" if brk else "❌",

        "Entry": round(entry, 2),
        "Stop": round(stop, 2),
        "Target": round(target, 2),
        "R/R": round(rr, 2),
    }

# ============================================================
# TIME (CST)
# ============================================================

cst = pytz.timezone("America/Chicago")
now = datetime.now(cst)

market_open = now.replace(hour=8, minute=30)
market_close = now.replace(hour=15, minute=0)

if market_open <= now <= market_close:
    st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

# ============================================================
# BANNER
# ============================================================

regime_text = "🟢 BULLISH" if SPY_REGIME else "🔴 BEARISH"
bg_color = "#1f7a1f" if SPY_REGIME else "#8b1a1a"

st.markdown(f"""
<div style="background-color:{bg_color};padding:12px;border-radius:10px;
color:white;font-size:18px;font-weight:600;text-align:center;">
Market Regime: {regime_text}
</div>
""", unsafe_allow_html=True)

st.caption(f"Last Refresh (CST): {now.strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================
# SCAN
# ============================================================

results = []

for s in SYMBOLS:
    try:
        df = get_data(s)
        df.attrs["symbol"] = s
        results.append(analyze(df))
    except:
        results.append({
            "Symbol": s,
            "Price": 0,
            "Score": 0,
            "Quality": "ERROR",
            "Trend": "❌",
            "Compression": "❌",
            "Volume": "❌",
            "Momentum": "❌",
            "Breakout": "❌",
            "Entry": 0,
            "Stop": 0,
            "Target": 0,
            "R/R": 0,
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

st.dataframe(df, use_container_width=True)