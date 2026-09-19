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
st.markdown("Scanner tehnic & fundamental complet pentru oportunități de Day Trading / Swing Trading (țintă 1-3%).")

# Sidebar - Filtre vizibile și configurabile
st.sidebar.header("⚙️ Filtre Tehnice & Fundamentale")

st.sidebar.subheader("1. Filtre Tehnice (Momentum)")
rsi_min = st.sidebar.slider("RSI Minim", 40, 70, 55)
rsi_max = st.sidebar.slider("RSI Maxim", 65, 85, 75)
vol_multiplier = st.sidebar.slider("Multiplicator Volum (vs Media 20z)", 1.0, 3.0, 1.2, 0.1)

st.sidebar.subheader("2. Filtre Fundamentale & Lichiditate")
min_market_cap_mld = st.sidebar.number_input("Capitalizare Minima (Miliarde $)", value=2.0, step=0.5)
min_avg_vol_m = st.sidebar.number_input("Volum Mediu Minim (Milioane)", value=1.0, step=0.5)
filter_pe = st.sidebar.checkbox("Doar companii profitabile (P/E > 0)", value=True)

# Lista extinsă de acțiuni US mari/lichide (S&P 100 / Nasdaq Top Movers)
TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD", "NFLX", 
    "AVGO", "COST", "PEP", "ADBE", "CRM", "INTC", "CSCO", "TMUS", "QCOM", 
    "TXN", "AMAT", "MU", "PANW", "SNPS", "CDNS", "KLAC", "ORCL", "NOW",
    "PLTR", "UBER", "ABNB", "SMCI", "COIN", "MARA", "SQ", "SHOP"
]

def scan_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        market_cap = info.get('marketCap', 0)
        forward_pe = info.get('forwardPE', None)
        avg_volume = info.get('averageVolume', 0)
        
        # Convertime în mld $ și mil acțiuni pentru verificare
        market_cap_mld = market_cap / 1e9 if market_cap else 0
        avg_volume_m = avg_volume / 1e6 if avg_volume else 0
        
        # Filtrare Fundamentală
        if market_cap_mld < min_market_cap_mld or avg_volume_m < min_avg_vol_m:
            return None
            
        if filter_pe and (forward_pe is None or forward_pe <= 0):
            return None

        # Preluare istoric preț
        hist = ticker.history(period="60d")
        if len(hist) < 50:
            return None

        # Calcul Variație Procentuală Zilnică (vs prețul de închidere din ziua anterioară)
        latest_close = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        pct_change = ((latest_close - prev_close) / prev_close) * 100

        # Indicatori Tehnici
        hist['EMA20'] = ta.trend.ema_indicator(hist['Close'], window=20)
        hist['EMA50'] = ta.trend.ema_indicator(hist['Close'], window=50)
        hist['RSI'] = ta.momentum.rsi(hist['Close'], window=14)

        latest = hist.iloc[-1]
        
        # Filtru Trend: Preț > EMA20 ȘI EMA20 > EMA50
        is_ema_bullish = (latest['Close'] > latest['EMA20']) and (latest['EMA20'] > latest['EMA50'])
        is_rsi_valid = rsi_min <= latest['RSI'] <= rsi_max
        
        vol_20_avg = hist['Volume'].tail(20).mean()
        vol_ratio_pct = round((latest['Volume'] / vol_20_avg) * 100, 1)
        is_vol_spike = latest['Volume'] > (vol_20_avg * vol_multiplier)

        # Condiție cumulativă
        if is_ema_bullish and is_rsi_valid and is_vol_spike:
            news_items = ticker.news[:2] if hasattr(ticker, 'news') and ticker.news else []
            headlines = " | ".join([n.get('title', '') for n in news_items]) if news_items else "Fără știri recente"

            return {
                "Ticker": symbol,
                "Preț Curent ($)": round(latest['Close'], 2),
                "Variație Ziua (%)": round(pct_change, 2),
                "EMA 20 ($)": round(latest['EMA20'], 2),
                "EMA 50 ($)": round(latest['EMA50'], 2),
                "RSI (14)": round(latest['RSI'], 1),
                "Volum vs Medie (%)": vol_ratio_pct,
                "Market Cap ($B)": round(market_cap_mld, 2),
                "P/E Forward": round(forward_pe, 1) if forward_pe else "N/A",
                "Știri / Catalizatori Recenți": headlines
            }
    except Exception:
        return None
    return None

# Funcție pentru stilizare culori text Variație
def style_variation(val):
    if isinstance(val, (int, float)):
        color = '#00c853' if val > 0 else '#ff1744' if val < 0 else '#888888'
        return f'color: {color}; font-weight: bold;'
    return ''

if st.button("🚀 Pornește Scanarea Completă", type="primary"):
    with st.spinner("Se analizează indicatorii tehnici, fundamentali și știrile..."):
        results = []
        progress_bar = st.progress(0)
        
        for idx, ticker in enumerate(TICKERS):
            res = scan_stock(ticker)
            if res:
                results.append(res)
            progress_bar.progress((idx + 1) / len(TICKERS))
            
        if results:
            df = pd.DataFrame(results)
            st.success(f"Au fost găsite {len(results)} acțiuni care îndeplinesc TOATE condițiile de momentum!")
            
            # Aplicare stilizare culori
            styled_df = df.style.map(style_variation, subset=['Variație Ziua (%)'])\
                                .format({'Variație Ziua (%)': '{:+.2f}%', 'Volum vs Medie (%)': '{:.1f}%'})
            
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("Nicio acțiune nu îndeplinește simultan toate criteriile stricte în acest moment. Încearcă să reduci puțin RSI-ul minim (ex: la 50) sau Multiplicatorul de Volum.")
