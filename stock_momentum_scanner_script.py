import yfinance as yf
import pandas as pd
import numpy as np

def get_sp500_tickers():
    """
    Descarcă automat lista tuturor companiilor din S&P 500 pentru a nu fi limitat la o listă fixă.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # Înlocuim punctele din simboluri (ex: BRK.B -> BRK-B) pentru compatibilitate cu yfinance
        tickers = [t.replace('.', '-') for t in tickers]
        return tickers
    except Exception as e:
        print(f"Eroare la preluarea listei S&P 500: {e}. Se folosește o listă de rezervă.")
        return ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD", "NFLX", "AVGO", "COST", "CRM"]

def analyze_stock(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        # 1. VERIFICARE FUNDAMENTALĂ & LICHIDITATE
        info = ticker.info
        market_cap = info.get('marketCap', 0)
        forward_pe = info.get('forwardPE', None)
        avg_volume = info.get('averageVolume', 0)
        
        # Filtru: Market Cap > 2 Mild $, Volum Mediu > 1M acțiuni, Companie Profitabilă (Forward P/E > 0)
        if market_cap < 2e9 or avg_volume < 1000000 or (forward_pe is None or forward_pe <= 0):
            return None

        # 2. VERIFICARE TEHNICĂ (MOMENTUM)
        hist = ticker.history(period="60d")
        if len(hist) < 50:
            return None

        # Calcul Madii Mobile Exponanțiale (EMA)
        hist['EMA20'] = hist['Close'].ewm(span=20, adjust=False).mean()
        hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
        
        # Calcul Relative Strength Index (RSI - 14)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))

        latest = hist.iloc[-1]

        # Condiții de Momentum:
        # - Preț peste EMA20 și EMA20 peste EMA50 (Trend crescător solid)
        # - RSI între 55 și 72 (Momentum fără supra-cumpărare extremă)
        # - Volum din ultima zi cu cel puțin 20% peste volumul mediu pe 20 zile
        avg_20_vol = hist['Volume'].tail(20).mean()
        is_ema_bullish = (latest['Close'] > latest['EMA20']) and (latest['EMA20'] > latest['EMA50'])
        is_rsi_momentum = 55 <= latest['RSI'] <= 72
        volume_spike = latest['Volume'] > (avg_20_vol * 1.2)

        if is_ema_bullish and is_rsi_momentum and volume_spike:
            # 3. EXTRASE ȘTIRI / CATALIZATORI
            news_items = ticker.news if hasattr(ticker, 'news') else []
            headlines = []
            if news_items:
                for item in news_items[:2]:
                    # Extragere titlu din structura Yahoo Finance
                    title = item.get('title') or item.get('content', {}).get('title', '')
                    if title:
                        headlines.append(title)
            
            if not headlines:
                headlines = ["Fără știri majore recente"]

            return {
                "Ticker": ticker_symbol,
                "Preț ($)": round(latest['Close'], 2),
                "RSI": round(latest['RSI'], 1),
                "Creștere Volum": f"{round((latest['Volume'] / avg_20_vol) * 100, 1)}%",
                "Catalizator Știri": " | ".join(headlines)
            }
    except Exception:
        return None
    return None

def main():
    print("🚀 Inițializare Scanner Momentum Acțiuni SUA...")
    tickers = get_sp500_tickers()
    print(f"📊 Se analizează {len(tickers)} acțiuni din S&P 500...\n")
    
    results = []
    for count, symbol in enumerate(tickers, 1):
        data = analyze_stock(symbol)
        if data:
            results.append(data)
            print(f"  [+] Găsit: {symbol} (RSI: {data['RSI']}, Preț: ${data['Preț ($)']})")
        
        # Status în consolă la fiecare 50 de acțiuni
        if count % 50 == 0:
            print(f"⏳ Progres: {count}/{len(tickers)} acțiuni procesate...")

    print("\n" + "="*80)
    if results:
        df = pd.DataFrame(results)
        print("✅ REZULTATE SCANARE (Oportunități Day / Swing Trading 1-3% Profit):")
        print("="*80)
        print(df.to_string(index=False))
        
        # Salvare rezultate în format CSV
        df.to_csv("rezultate_momentum.csv", index=False)
        print("\n📁 Rezultatele au fost salvate și în fișierul 'rezultate_momentum.csv'.")
    else:
        print("❌ Nicio acțiune nu îndeplinește în acest moment toate condițiile stricte de momentum.")
    print("="*80)

if __name__ == "__main__":
    main()