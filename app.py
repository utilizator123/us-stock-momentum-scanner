import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(
    page_title="US Stock Momentum Scanner",
    page_icon="📈",
    layout="wide"
)

st.title("📈 US Stock Momentum Scanner")
st.markdown("Scanner tehnic & fundamental pentru oportunități de Day Trading / Swing Trading (țintă 1-3%).")

# Sidebar - Filtre
st.sidebar.header("Parametri Filtrare")

rsi_min = st.sidebar.slider("RSI Minim", 40, 70, 55)
rsi_max = st.sidebar.slider("RSI Maxim", 65, 85, 75)
vol_multiplier = st.sidebar.slider("Multiplicator Volum (vs Media 20z)", 1.0, 3.0, 1.2, 0.1)
min_market_cap = st.sidebar.number_input("Capitalizare Minima ($)", value=2000000000, step=500000000)
min_avg_vol = st.sidebar.number_input("Volum Mediu Minim", value=1000000, step=100000)

TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD", "NFLX", 
    "AVGO", "COST", "PEP", "ADBE", "CRM", "INTC", "CSCO", "TMUS", "QCOM", 
    "TXN", "AMAT", "MU", "PANW", "SNPS", "CDNS", "KLAC", "ORCL", "NOW"
]

def scan_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        market_cap = info.get('marketCap', 0)
        forward_pe = info.get('forwardPE', None)
        avg_volume = info.get('averageVolume', 0)
        
        if market_cap < min_market_cap or avg_volume < min_avg_vol:
            return None
        if forward_pe is None or forward_pe <= 0:
            return None

        hist = ticker.history(period="60d")
        if len(hist) < 50:
            return None

        hist['EMA20'] = ta.trend.ema_indicator(hist['Close'], window=20)
        hist['EMA50'] = ta.trend.ema_indicator(hist['Close'], window=50)
        hist['RSI'] = ta.momentum.rsi(hist['Close'], window=14)

        latest = hist.iloc[-1]
        
        is_ema_bullish = (latest['Close'] > latest['EMA20']) and (latest['EMA20'] > latest['EMA50'])
        is_rsi_valid = rsi_min <= latest['RSI'] <= rsi_max
        
        vol_20_avg = hist['Volume'].tail(20).mean()
        is_vol_spike = latest['Volume'] > (vol_20_avg * vol_multiplier)

        if is_ema_bullish and is_rsi_valid and is_vol_spike:
            news_items = ticker.news[:2] if hasattr(ticker, 'news') and ticker.news else []
            headlines = " | ".join([n.get('title', '') for n in news_items]) if news_items else "Fără știri recente"
            
            return {
                "Ticker": symbol,
                "Preț ($)": round(latest['Close'], 2),
                "RSI (14)": round(latest['RSI'], 1),
                "Creștere Volum": f"{round((latest['Volume'] / vol_20_avg) * 100, 1)}%",
                "P/E Forward": round(forward_pe, 1) if forward_pe else "N/A",
                "Știri / Catalizatori": headlines
            }
    except Exception:
        return None
    return None

if st.button("🚀 Pornește Scanarea", type="primary"):
    with st.spinner("Se analizează piața..."):
        results = []
        progress_bar = st.progress(0)
        
        for idx, ticker in enumerate(TICKERS):
            res = scan_stock(ticker)
            if res:
                results.append(res)
            progress_bar.progress((idx + 1) / len(TICKERS))
            
        if results:
            df = pd.DataFrame(results)
            st.success(f"Au fost găsite {len(results)} acțiuni cu momentum optim!")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Nicio acțiune nu îndeplinește toate condițiile în acest moment. Încearcă să reduci RSI-ul minim sau multiplicatorul de volum.")
