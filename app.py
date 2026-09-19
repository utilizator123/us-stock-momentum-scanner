import streamlit as st
import yfinance as yf
import pandas as pd

# Setări Pagina Web
st.set_page_config(
    page_title="US Stock Momentum Scanner",
    page_icon="📈",
    layout="wide"
)

st.title("📈 US Stock Momentum Scanner")
st.markdown("""
Aplicație pentru identificarea oportunităților de **Day Trading / Swing Trading (1-3% Profit)** pe piața din SUA (S&P 500).
""")

# Bara Laterală (Filtre Interactive)
st.sidebar.header("⚙️ Setări & Filtre Momentum")

min_market_cap = st.sidebar.number_input("Market Cap Minim ($)", value=2000000000, step=1000000000, format="%d")
min_volume = st.sidebar.number_input("Volum Mediu Minim (Acțiuni)", value=1000000, step=500000)

rsi_min, rsi_max = st.sidebar.slider("Interval RSI (14)", 0, 100, (55, 72))
vol_multiplier = st.sidebar.slider("Multiplicator Volum vs Media 20-Zile", 1.0, 3.0, 1.2, step=0.1)

@st.cache_data(ttl=3600)
def get_sp500_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]
        tickers = [t.replace('.', '-') for t in df['Symbol'].tolist()]
        return tickers
    except Exception:
        return ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD", "NFLX", "AVGO"]

def analyze_stock(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        market_cap = info.get('marketCap', 0)
        forward_pe = info.get('forwardPE', None)
        avg_volume = info.get('averageVolume', 0)
        
        if market_cap < min_market_cap or avg_volume < min_volume or (forward_pe is None or forward_pe <= 0):
            return None

        hist = ticker.history(period="60d")
        if len(hist) < 50:
            return None

        hist['EMA20'] = hist['Close'].ewm(span=20, adjust=False).mean()
        hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
        
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))

        latest = hist.iloc[-1]
        avg_20_vol = hist['Volume'].tail(20).mean()

        is_ema_bullish = (latest['Close'] > latest['EMA20']) and (latest['EMA20'] > latest['EMA50'])
        is_rsi_momentum = rsi_min <= latest['RSI'] <= rsi_max
        volume_spike = latest['Volume'] > (avg_20_vol * vol_multiplier)

        if is_ema_bullish and is_rsi_momentum and volume_spike:
            news_items = ticker.news if hasattr(ticker, 'news') else []
            headlines = []
            if news_items:
                for item in news_items[:2]:
                    title = item.get('title') or item.get('content', {}).get('title', '')
                    if title:
                        headlines.append(title)
            
            return {
                "Ticker": ticker_symbol,
                "Preț ($)": round(latest['Close'], 2),
                "RSI": round(latest['RSI'], 1),
                "Creștere Volum": f"{round((latest['Volume'] / avg_20_vol) * 100, 1)}%",
                "Catalizator Știri": " | ".join(headlines) if headlines else "Fără știri recente"
            }
    except Exception:
        return None
    return None

# Buton Rulare
if st.button("🚀 Porneste Scanarea Pieței"):
    tickers = get_sp500_tickers()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    total_tickers = len(tickers)
    
    for i, symbol in enumerate(tickers):
        status_text.text(f"Analizăm {symbol} ({i+1}/{total_tickers})...")
        data = analyze_stock(symbol)
        if data:
            results.append(data)
        progress_bar.progress((i + 1) / total_tickers)
        
    status_text.empty()
    progress_bar.empty()
    
    if results:
        df = pd.DataFrame(results)
        st.success(f"✅ Am găsit {len(df)} acțiuni cu Momentum!")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("❌ Nicio acțiune nu îndeplinește criteriile selectate în acest moment.")
```

---

### Pasul 2: Fișierul de Cerințe `requirements.txt`

Pentru ca platforma cloud să știe ce module Python să instaleze, creează un fișier numit `requirements.txt`:

```text:Requirements File:requirements.txt
streamlit
yfinance
pandas
numpy
lxml
```

---

### Pasul 3: Cum publici aplicația pentru a obține Link-ul Direct (Gratuit)

Pentru a găzdui aplicația gratuit fără GitHub clasic, poți folosi **Hugging Face Spaces** sau **Streamlit Community Cloud**:

#### Metoda Hugging Face Spaces (Cea mai ușoară, fără comenzi Git):
1. Creează-ți un cont gratuit pe [HuggingFace.co](https://huggingface.co/).
2. Apasă pe profilul tău sus în dreapta -> **New Space**.
3. Pune un nume proiectului (ex: `my-momentum-scanner`).
4. La **Select the Space SDK**, alege **Streamlit**.
5. Apasă **Create Space**.
6. În pagina nouă, apasă pe tab-ul **Files** -> **Add file** -> **Upload files**.
7. Încarcă cele două fișiere create mai sus: `app.py` și `requirements.txt`.
8. Apasă **Commit changes to main**.

Aplicația se va construi automat în 1-2 minute, iar la final vei primi un **link public permanent** (de forma `https://huggingface.co/spaces/Utilizator/my-momentum-scanner`) pe care îl poți salva în browser și accesa oricând de pe telefon sau calculator!
