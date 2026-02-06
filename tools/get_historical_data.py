from langchain_core.tools import tool
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
import yfinance as yf

# Define the Enum for valid periods
class PeriodEnum(str, Enum):
    one_day = '1d'
    five_days = '5d'
    one_month = '1mo'
    three_months = '3mo'
    six_months = '6mo'
    one_year = '1y'
    two_years = '2y'
    five_years = '5y'
    ten_years = '10y'
    year_to_date = 'ytd'
    max_period = 'max'

# Define the input schema with optional and enum fields
class HistoricalDataInput(BaseModel):
    ticker: str = Field(..., description="The ticker symbol of the stock to fetch historical data for")
    period: Optional[PeriodEnum] = Field(PeriodEnum.one_month, description="The period for which to fetch historical data")

@tool(args_schema=HistoricalDataInput)
def get_historical_data(ticker: str, period: str = "1mo") -> dict:
    """Fetch historical market data for a given ticker symbol and period (1d, 5d, 1mo, etc.)."""
    
    # Ensure ticker has the correct suffix for Indian markets if needed
    formatted_ticker = f"{ticker}.NS" if not ticker.endswith(".NS") else ticker
    stock = yf.Ticker(formatted_ticker)
    
    # Fetch history using the validated period string
    history = stock.history(period=period)
    
    if history.empty:
        return {"error": f"No data found for {ticker} in period {period}"}
    
    # Convert index (Dates) to string for JSON serialization
    history.index = history.index.strftime('%Y-%m-%d %H:%M:%S')
    return history.to_dict(orient='index')