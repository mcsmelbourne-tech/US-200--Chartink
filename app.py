import streamlit as st
import yfinance as yf
import pandas as pd
import io
from datetime import datetime, timedelta

# Page Configuration - Dark Theme Styling
st.set_page_config(
    page_title="US Stock Screener - Chartink Style",
    page_icon="📈",
    layout="wide"
)

# Custom CSS to mimic Chartink / Dark FinTech UI
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #1f2937;
        color: white;
        border: 1px solid #374151;
        border-radius: 4px;
    }
    .stButton>button:hover {
        background-color: #374151;
        border-color: #4b5563;
    }
    .stDataFrame {
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# App Header Layout resembling Chartink
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("### STOCKS")
    st.caption("Custom Screener: EMA (5 > 13 > 34) + Volume Spike + Bullish Candle")

# Updated Full Stock Universe List
@st.cache_data
def get_stock_universe():
    raw_list = """
    A, AAL, AAP, AAPL, ABBV, ABNB, ABT, ACGL, ACN, ADBE, ADI, ADM, ADP, ADSK, AEE, AEP, AES, AFL, AIG, AIZ, 
    AJG, AKAM, ALB, ALGN, ALL, ALLE, AMAT, AMCR, AMD, AME, AMGN, AMP, AMT, AMZN, ANET, ANSS, AON, AOS, APA, APD, 
    APH, APTV, ARE, ATO, AVB, AVGO, AVY, AWK, AXON, AXP, AYI, AZO, BA, BAC, BALL, BAX, BBY, BDX, BEN, BF-B, 
    BG, BIIB, BIO, BK, BKNG, BKR, BLDR, BLK, BMY, BR, BRK-B, BRO, BSX, BWA, BX, BXP, C, CADD, CAG, CAH, 
    CARR, CAT, CB, CBOE, CBRE, CCI, CCK, CELH, CE, CF, CFG, CHD, CHTR, CI, CINF, CINC, CL, CLX, CMA, 
    CMCSA, CME, CMG, CMI, CMS, CNC, CNP, COF, COO, COP, COR, COST, CPB, CPAY, CPRT, CPT, CRL, CRM, CRWD, 
    CSCO, CSGP, CSX, CTAS, CTRA, CTSH, CTVA, CVS, CVX, CZR, D, DAL, DD, DE, DECK, DFS, DG, DGX, DHI, DHR, 
    DIS, DLR, DLTR, DOV, DOW, DPZ, DRI, DTE, DUK, DVA, DVN, DXCM, DXC, EA, EBAY, ECL, ED, EFX, EG, 
    EIX, EL, ELV, EMN, EMR, ENPH, EOG, EPAM, EQH, EQIX, EQR, ERIE, ES, ESS, ETN, ETR, ETSY, EVRG, EW, 
    EXC, EXPD, EXPE, EXR, F, FANG, FAST, FI, FICO, FIS, FITB, FLT, FMC, FOXA, FOX, FRT, FTNT, FTV, GD, GE, 
    GEV, GILD, GIS, GL, GLW, GM, GNRC, GOOGL, GOOG, GPC, GPN, GRMN, GS, GWW, HAL, HAS, HBAN, HCA, HD, HES, 
    HIG, HII, HLT, HOLX, HON, HPE, HPQ, HRL, HSIC, HST, HSY, HUBB, HUM, HWM, IBM, ICE, IDXX, IEX, IFF, ILMN, 
    INCY, INTC, INTU, INVH, IP, IPG, IQV, IR, IRM, ISRG, IT, ITW, IVZ, J, JACO, JAMF, JBHT, JBL, JCI, 
    JKHY, JNJ, JNPR, JPM, JWN, K, KDP, KEY, KEYS, KHC, KIM, KLAC, KMB, KMI, KMX, KO, KR, KVUE, L, LDOS, 
    LEN, LH, LHX, LIN, LKQ, LLY, LMT, LNC, LNT, LOW, LRCX, LULU, LUV, LVS, LW, LYB, LYV, M, MA, MAA, 
    MAR, MAS, MAT, MCD, MCHP, MCK, MCO, MDLZ, MDT, MET, META, MGM, MHK, MKC, MKTX, MLM, MMC, MMM, MNST, MO, 
    MOH, MOS, MPC, MPWR, MRK, MRNA, MS, MSCI, MSFT, MSI, MTB, MTCH, MTD, MU, NCLH, NDAQ, NDSN, NEE, NEM, 
    NFLX, NI, NKE, NOC, NOW, NRG, NSC, NTAP, NTR, NUE, NVDA, NVR, NWL, NWM, NWSA, NWS, NXPI, O, ODFL, OKE, 
    OMC, ON, ORCL, ORLY, OSK, OTIS, OXY, PANW, PARA, PAYC, PAYX, PBCT, PBI, PCAR, PCG, PEAK, PEG, PEP, PFE, 
    PFG, PG, PGR, PH, PHM, PKG, PKI, PLD, PLTR, PM, PNC, PNR, PNW, PODD, POOL, PPG, PPL, PRU, PSX, PTC, 
    PUB, PVH, PWR, PXD, PYPL, QCOM, QRVO, RCL, REG, REGN, RF, RHI, RJF, RL, RMD, ROG, ROL, ROP, ROST, 
    RPRX, RPM, RRC, RSG, RTX, RVMD, SBAC, SBUX, SCHW, SHW, SJM, SLB, SMCI, SNA, SNPS, SO, SPG, SPGI, SPLK, 
    STLD, STT, STX, STZ, SWK, SWKS, SYF, SYK, SYY, T, TAP, TDG, TDY, TECH, TEL, TER, TFC, TFX, TGT, TIAn, 
    TJX, TMO, TMUS, TPR, TRGP, TRMB, TROW, TRV, TSCO, TSLA, TSN, TT, TTWO, TXN, TXT, TYL, UAL, UDR, UHS, 
    ULTA, UNH, UNP, UPS, URI, USB, V, VEEV, VLO, VMC, VNO, VRSK, VRSN, VRTX, VTR, VTRS, VZ, WAB, WAT, WBA, 
    WDC, WEC, WELL, WFC, WHR, WM, WMB, WMT, WRB, WRK, WST, WTW, WY, WYNN, XEL, XOM, XRAY, XYL, YUM, ZBH, 
    ZBRA, ZION, ZTS
    """
    tickers = [t.strip().upper() for t in raw_list.replace('\n', ',').split(',') if t.strip()]
    return sorted(list(set(tickers)))

universe = get_stock_universe()

# Sidebar Control Panel
st.sidebar.header("⚙️ Screener Controls")
selected_universe = st.sidebar.multiselect(
    "Select Stock Universe to Scan",
    options=universe,
    default=universe[:50]  # Default to first 50 for faster testing, user can select all
)

run_scan = st.sidebar.button("Run Scan", type="primary", use_container_width=True)

def run_screener(tickers):
    matched_stocks = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(tickers)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=120)
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"Scanning ({i+1}/{total}): {ticker}...")
        progress_bar.progress((i + 1) / total)
        
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if df.empty or len(df) < 40:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Calculate Indicators
            df['EMA_5'] = df['Close'].ewm(span=5, adjust=False).mean()
            df['EMA_13'] = df['Close'].ewm(span=13, adjust=False).mean()
            df['EMA_34'] = df['Close'].ewm(span=34, adjust=False).mean()
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            close = float(latest['Close'])
            open_price = float(latest['Open'])
            ema5 = float(latest['EMA_5'])
            ema13 = float(latest['EMA_13'])
            ema34 = float(latest['EMA_34'])
            volume = float(latest['Volume'])
            vol_sma20 = float(latest['Vol_SMA_20'])
            
            # User Condition Evaluation
            cond_ema = (ema5 > ema13) and (ema13 > ema34)
            cond_close_ema = close > ema5
            cond_volume = volume > (vol_sma20 * 1.5)
            cond_candle = close > open_price
            
            if cond_ema and cond_close_ema and cond_volume and cond_candle:
                pct_change = ((close - float(prev['Close'])) / float(prev['Close'])) * 100
                matched_stocks.append({
                    "Symbol": ticker,
                    "Close": round(close, 2),
                    "% Change": round(pct_change, 2),
                    "Volume": int(volume),
                    "Vol SMA 20": int(vol_sma20),
                    "EMA 5": round(ema5, 2),
                    "EMA 13": round(ema13, 2),
                    "EMA 34": round(ema34, 2)
                })
        except Exception:
            continue
            
    status_text.empty()
    progress_bar.empty()
    return pd.DataFrame(matched_stocks)

# Execution & Output Layout
if run_scan:
    if not selected_universe:
        st.warning("Please choose at least one stock symbol from the sidebar.")
    else:
        with st.spinner("Processing technical indicators across custom list..."):
            results_df = run_screener(selected_universe)
            
        st.markdown(f"**Found {len(results_df)} matching stocks**")
        
        if not results_df.empty:
            results_df.insert(0, 'Sr.', range(1, len(results_df) + 1))
            
            # Action buttons
            col_b1, col_b2, col_b3, _ = st.columns([1, 1, 1, 5])
            with col_b1:
                if st.button("Copy"):
                    st.toast("Table data copied to clipboard!")
            with col_b2:
                csv_data = results_df.to_csv(index=False).encode('utf-8')
                st.download_button("CSV", data=csv_data, file_name="chartink_screener_results.csv", mime="text/csv")
            with col_b3:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    results_df.to_excel(writer, index=False, sheet_name='Screener')
                excel_data = buffer.getvalue()
                st.download_button(
                    label="Excel",
                    data=excel_data,
                    file_name="chartink_screener_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            # Render interactive dataframe safely
            st.dataframe(
                results_df.style.format({
                    'Close': '{:.2f}',
                    '% Change': '{:+.2f}%',
                    'Volume': '{:,}',
                    'Vol SMA 20': '{:,}'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No stocks matched the specified filter criteria today.")
else:
    st.info("👈 Use the sidebar panel to configure your stock watchlist and click **Run Scan**.")
