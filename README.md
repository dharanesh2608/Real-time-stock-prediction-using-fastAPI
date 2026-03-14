# 📈 Real-Time Stock Prediction using FastAPI

An AI-powered **Stock Prediction and Trading Recommendation API** built with **FastAPI**.
The system fetches **real-time stock data from Yahoo Finance**, analyzes technical indicators, and generates **BUY / SELL / HOLD predictions** with confidence scores.

---

# 🔗 Repository

GitHub Repo:

https://github.com/dharanesh2608/Real-time-stock-prediction-using-fastAPI

---

# 🖼️ Project Preview

## API Documentation (Swagger UI)

![Swagger UI](images/api_docs.png)

---

## Stock Data Fetch Example

![Stock Data](images/stock_data.png)

---

## Prediction Output

![Prediction Output](images/prediction_output.png)

---

# 🚀 Features

* 📊 Fetch **real-time stock market data**
* 📈 Calculate **technical indicators**
* 🤖 Generate **AI-based trading signals**
* 📉 Predict **stock price movement**
* 🎯 Provide **confidence score**
* 🔍 Validate stock symbols
* 🧪 Run **backtesting simulations**
* ❤️ API **health monitoring**

---

# 🧠 Technical Indicators Used

The prediction engine uses multiple technical indicators:

• **RSI (Relative Strength Index)** – momentum indicator
• **MACD (Moving Average Convergence Divergence)** – trend analysis
• **SMA 20 / SMA 50** – moving averages
• **EMA 20** – exponential moving average
• **ATR** – volatility indicator
• **OBV** – volume trend indicator

These indicators are combined to generate trading signals.

---

# 🏗️ System Architecture

```
Client Request
      │
      ▼
FastAPI API Server
      │
      ▼
Yahoo Finance API (yfinance)
      │
      ▼
Technical Indicator Engine
      │
      ▼
Trading Signal Generator
      │
      ▼
Prediction Response
(BUY / SELL / HOLD)
```

---

# 📂 Project Structure

```
Real-time-stock-prediction-using-fastAPI
│
├── main.py
├── README.md
├── requirements.txt
│
└── images
    ├── api_docs.png
    ├── prediction_output.png
    └── stock_data.png
```

---

# ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/dharanesh2608/Real-time-stock-prediction-using-fastAPI.git
cd Real-time-stock-prediction-using-fastAPI
```

---

### Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

Windows

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install fastapi uvicorn pandas numpy yfinance
```

---

# ▶️ Running the API

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Server runs at:

```
http://localhost:8000
```

Swagger documentation:

```
http://localhost:8000/docs
```

---

# 🔗 API Endpoints

### Root

```
GET /
```

Returns API status.

---

### Fetch Stock Data

```
POST /fetch-data
```

Example request:

```json
{
  "symbol": "AAPL",
  "days": 30
}
```

---

### Predict Stock Movement

```
POST /predict
```

Example request:

```json
{
  "symbol": "AAPL"
}
```

Example response:

```json
{
 "symbol": "AAPL",
 "current_price": 187.24,
 "prediction": "UP",
 "confidence": 0.72,
 "recommendation": "BUY"
}
```

---

### Validate Symbol

```
POST /validate-symbol
```

Checks whether a stock symbol exists.

---

### Backtesting

```
POST /backtest
```

Simulates strategy performance.

---

### Health Check

```
GET /health
```

Returns API health status.

---

# 🛠️ Technologies Used

* **Python**
* **FastAPI**
* **Pandas**
* **NumPy**
* **Yahoo Finance (yfinance)**
* **Uvicorn**

---

# 🔮 Future Improvements

* Machine learning models (LSTM / Transformers)
* Real-time stock streaming
* Web dashboard visualization
* Portfolio optimization
* Risk analysis module

---

# ⚠️ Disclaimer

This project is intended **for educational purposes only**.
It should **not be considered financial advice**.

---

# ⭐ Support

If you like this project, please **⭐ star the repository**.
