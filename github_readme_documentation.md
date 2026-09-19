# 📈 US Stock Momentum Scanner (Day & Swing Trading)

Un script Python creat pentru identificarea rapidă a acțiunilor din piața Americană (S&P 500) care se află într-o fază clară de **momentum crescător**, susținute de indicatori tehnici, date fundamentale solide și știri recente (catalizatori).

Conceput special pentru idei de tranzacționare rapidă (**Day Trading / Swing Trading de 1-3 zile**) cu un obiectiv de profit de **1% - 3% per tranzacție**.

---

## 🚀 Rulare Directă în Browser (Fără Instalare)

Apasă pe butonul de mai jos pentru a deschide și rula scannerul direct în **Google Colab**:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/USERNAME/REPOSITORY/blob/main/stock_momentum_scanner.py)

*(Notă: Înlocuiește `USERNAME/REPOSITORY` din linkul de mai sus cu numele tău de utilizator și repozitoriul tău de GitHub după upload).*

---

## 📊 Criterii de Filtrare

### 1. Filtru Fundamental & Lichiditate (Stabilitate)
* **Market Capitalization**: Peste \$2 Miliarde (Elimină acțiunile foarte volatile / penny stocks).
* **Volum Mediu**: Peste 1.000.000 de acțiuni tranzacționate zilnic (Garantează o intrare și ieșire rapidă din tranzacție).
* **Profitabilitate**: Forward P/E Pozitiv.

### 2. Filtru Tehnic (Momentum)
* **Trend**: Prețul peste EMA 20, iar EMA 20 peste EMA 50 ($Price > EMA_{20} > EMA_{50}$).
* **RSI (14)**: Între **55 și 72** (Indicator de forță fără a fi extrem de supra-cumpărat).
* **Volum Spike**: Volumul din ultima zi este cu cel puțin **20% peste media ultimelor 20 de zile** (Semnal de achiziție instituțională).

### 3. Catalizator Știri
* Extrage ultimele titluri de știri relevante pentru fiecare ticker găsit, oferind contextul fundamental al creșterii.

---

## 💻 Rulare Locală (Pe calculatorul tău)

Dacă dorești să rulezi scriptul local:

1. Clonează repozitoriul:
   ```bash
   git clone https://github.com/USERNAME/REPOSITORY.git
   cd REPOSITORY
   ```

2. Instalează dependențele:
   ```bash
   pip install yfinance pandas numpy lxml
   ```

3. Rulează scannerul:
   ```bash
   python stock_momentum_scanner.py
   ```

---

## ⚠️ Disclaimer
Acest cod este realizat exclusiv în scop informativ și educațional. Tranzacționarea pe bursă implică riscuri financiare. Setați întotdeauna un **Stop Loss (ex: -1%)** pentru a vă proteja capitalul.