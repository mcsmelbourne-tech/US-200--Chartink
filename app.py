import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="US Stock Screener (Chartink Style)",
    page_icon="📈",
    layout="wide"
)

# App Header
st.title("📈 US Stock Momentum Screener")
st.markdown("""
This screener evaluates US stocks based on your custom criteria:
* **EMA Alignment:** Daily EMA 5 > EMA 13 > EMA 34
* **Price Position:** Daily Close > EMA 5 and Daily Close > Daily Open (Bullish Candle)
* **Volume Spike:** Daily Volume > 20-period Volume SMA $\times$ 1.5
""")

# Pre-defined list of liquid US stocks (Universe sample - can be expanded)
@st.cache_data
def get_stock_universe():
    return [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "COST", "NFLX",
        "AMD", "QCOM", "TMUS", "INTC", "AMAT", "CMCSA", "PEP", "ADBE", "TXN", "AMGN",
        "HON", "IBM", "SBUX", "GILD", "INTU", "MDLZ", "BKNG", "ISRG", "ADI", "VRTX",
        "LRCX", "PYPL", "MU", "REGN", "PDD", "SNPS", "CDNS", "PANW", "ASML", "MAR",
        "MELI", "CSX", "ORLY", "CTAS", "MNST", "ABNB", "ROP", "WDAY", "DXCM", "AEP",
        "PLTR", "CRWD", "DDOG", "NET", "COIN", "HOOD", "RIVN", "LCID", "SOFI", "DKNG",
        "RBLX", "SHOP", "UBER", "LYFT", "ABNB", "DASH", "PINS", "SNAP", "SQ", "ENPH"
    ]

universe = get_stock_universe()

# Sidebar Controls
st.sidebar.header("Screener Settings")
selected_universe = st.sidebar.multiselect(
    "Stock Universe",
    options=universe,
    default=universe[:40] # Default to first 40 for speed
)

run_button = st.sidebar.button("Run Screener", type="primary")

def run_screener(tickers):
    matched_stocks = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(tickers)
    
    # Fetch data for the last 3 months to ensure enough bars for 34 EMA & 20 SMA
    end_date = datetime.today()
    start_date = end_date - timedelta(days=120)
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"Scanning ({i+1}/{total}): {ticker}...")
        progress_bar.progress((i + 1) / total)
        
        try:
            # Download daily data
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if df.empty or len(df) < 40:
                continue
                
            # Handle MultiIndex columns if returned by newer yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Calculate Indicators
            df['EMA_5'] = df['Close'].ewm(span=5, adjust=False).mean()
            df['EMA_13'] = df['Close'].ewm(span=13, adjust=False).mean()
            df['EMA_34'] = df['Close'].ewm(span=34, adjust=False).mean()
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            
            # Get latest row
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            close = latest['Close']
            open_price = latest['Open']
            ema5 = latest['EMA_5']
            ema13 = latest['EMA_13']
            ema34 = latest['EMA_34']
            volume = latest['Volume']
            vol_sma20 = latest['Vol_SMA_20']
            
            # Check Conditions:
            # 1. EMA 5 > EMA 13 > EMA 34
            cond_ema = (ema5 > ema13) and (ema13 > ema34)
            # 2. Close > EMA 5
            cond_price_ema = close > ema5
            # 3. Volume > SMA(Volume, 20) * 1.5
            cond_vol = volume > (vol_sma20 * 1.5)
            # 4. Close > Open (Bullish candle)
            cond_candle = close > open_price
            
            if cond_ema and cond_price_ema and cond_vol and cond_candle:
                matched_stocks.append({
                    "Ticker": ticker,
                    "Close": round(float(close), 2),
                    "Open": round(float(open_price), 2),
                    "Change %": round(float(((close - prev['Close']) / prev['Close']) * 100), 2),
                    "Volume": int(volume),
                    "Vol SMA 20": int(vol_sma20),
                    "EMA 5": round(float(ema5), 2),
                    "EMA 13": round(float(ema13), 2),
                    "EMA 34": round(float(ema34), 2)
                })
        except Exception as e:
            continue
            
    status_text.text("Scan complete!")
    progress_bar.empty()
    return pd.DataFrame(matched_stocks)

# Main Execution Flow
if run_button:
    if not selected_universe:
        st.warning("Please select at least one stock to scan.")
    else:
        with st.spinner("Running technical analysis across selected tickers..."):
            results_df = run_screener(selected_universe)
            
        st.subheader(f"Results Found: {len(results_df)}")
        
        if not results_df.empty:
            st.dataframe(results_df, use_container_width=True)
            
            # CSV Download Button
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"stock_screener_{datetime.today().strftime('%Y-%m-%d')}.csv",
                mime='text/csv',
            )
        else:
            st.info("No stocks matched your criteria today.")
else:
    st.info("👈 Configure your universe in the sidebar and click **Run Screener** to begin.")
