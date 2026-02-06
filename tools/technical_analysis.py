import pandas as pd
import numpy as np

def calculate_technicals(history_data):
    """
    Takes raw historical data (list of dicts or dict of dicts) and returns 
    a pandas DataFrame with computed technical indicators suitable for Day Trading.
    """
    try:
        # Convert the dictionary input to DataFrame
        if isinstance(history_data, dict) and 'error' not in history_data:
            # Handle the format returned by yfinance to_dict('index')
            df = pd.DataFrame.from_dict(history_data, orient='index')
        elif isinstance(history_data, list):
            df = pd.DataFrame(history_data)
        else:
            return {"error": "Invalid data format for technical analysis"}

        # Ensure numeric columns
        cols = ['Close', 'High', 'Low', 'Volume']
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if df.empty:
            return {"error": "Empty dataframe"}

        # Sort by date
        df.sort_index(inplace=True)

        # --- INDICATOR CALCULATIONS ---

        # 1. RSI (Relative Strength Index) - 14 period
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 2. MACD (Moving Average Convergence Divergence)
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # 3. Bollinger Bands (20 SMA, 2 std dev)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['BB_Upper'] = df['SMA_20'] + (df['Close'].rolling(window=20).std() * 2)
        df['BB_Lower'] = df['SMA_20'] - (df['Close'].rolling(window=20).std() * 2)

        # 4. Volume Trend
        df['Vol_SMA_5'] = df['Volume'].rolling(window=5).mean()
        
        # 5. EMA (Exponential Moving Averages)
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()

        # Extract the latest data point (The "Current" state)
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Generate a textual summary for the LLM
        signal_summary = {
        "current_price": float(round(latest['Close'], 2)),
        "rsi": float(round(latest['RSI'], 2)),
        "macd_crossover": "Bullish" if latest['MACD'] > latest['Signal_Line'] and prev['MACD'] <= prev['Signal_Line'] else "Bearish" if latest['MACD'] < latest['Signal_Line'] else "Neutral",
        "trend_ema": "Uptrend" if latest['Close'] > latest['EMA_20'] else "Downtrend",
        "bollinger_position": "Overbought" if latest['Close'] > latest['BB_Upper'] else "Oversold" if latest['Close'] < latest['BB_Lower'] else "Neutral",
        "volume_status": "High" if latest['Volume'] > latest['Vol_SMA_5'] else "Normal"
}
        return signal_summary

    except Exception as e:
        return {"error": f"Technical analysis failed: {str(e)}"}