# 📈 Kalman Filter High-Frequency Trading Strategy

## 📌 Overview
This project implements a **High-Frequency Trading (HFT)** strategy using a **Kalman Filter** to estimate the "true" market price from noisy live tick data.  
It connects to **Upstox V3 WebSocket Market Data Feed**, processes **real-time LTP updates**, and generates buy/sell signals based on the deviation between the Kalman Filter estimate and the observed price.  

It can also place simulated orders in the **Upstox Sandbox environment** for safe testing.

---

## 🚀 Features
- Real-time market data via **Upstox V3 WebSocket**
- **Kalman Filter** implementation for price smoothing
- Automatic **BUY/SELL signal generation**
- **End-of-Day position closing** before market close
- Trade logging to `trades.csv`
- Structured logging to console and `strategy.log`
- Modular, maintainable Python code

---

## 📂 Project Structure
- ├── config.py # API tokens, instrument details, trade quantity
- ├── kalman.py # Kalman Filter implementation
- ├── logger.py # Logging utility
- ├── main.py # Main strategy logic
- ├── trader.py # Order placement & trade logging
- ├── MarketDataFeedV3_pb2.py # Protobuf parser for Upstox feed
- ├── requirements.txt # Python dependencies
- ├── strategy.log # Runtime logs (generated)
- ├── trades.csv # Trade history (generated)
- └── README.md # Project documentation 


---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository

git clone https://github.com/yourusername/kalman-hft-strategy.git
cd kalman-hft-strategy

---

## 📡 How It Works
- Authorize Feed – Retrieves feed authorization from Upstox API

- Connect to WebSocket – Subscribes to live market data for the selected instrument

- Kalman Filter Update – Processes each incoming tick to estimate the true price

- Signal Generation – Compares estimated price with LTP:

- BUY if estimate is significantly higher than LTP

- SELL if estimate is significantly lower than LTP

- Trade Execution – Sends market orders via Upstox Sandbox API

- Trade Logging – Saves all trades to trades.csv

---

## 📊 Example Output
[2025-08-14 10:00:01] Starting Kalman strategy...
[2025-08-14 10:00:02] WebSocket connected...
[2025-08-14 10:00:03] Subscription sent for: NSE_FO|55775
[2025-08-14 10:01:45] Tick 105 | Price ₹453.25 | KF ₹453.75
[2025-08-14 10:01:46] BUY SIGNAL | RelDiff 0.00111
[2025-08-14 10:01:47] BUY ORDER RESPONSE: {"status":"success"}
---
##📦 Dependencies
The project requires:
- numpy
- websockets
- requests
- google.protobuf



