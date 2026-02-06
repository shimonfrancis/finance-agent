from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class RiskTolerance(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"

class InvestmentGoal(str, Enum):
    growth = "growth"
    income = "income"
    value = "value"
    balanced = "balanced"

class StockSuggesterInput(BaseModel):
    risk_tolerance: RiskTolerance = Field(..., description="User's risk tolerance level")
    investment_goal: InvestmentGoal = Field(..., description="User's investment objective")
    budget: Optional[float] = Field(None, description="Available investment amount in USD")
    sectors: Optional[List[str]] = Field(None, description="Preferred sectors to invest in")
    max_suggestions: int = Field(5, description="Maximum number of stock suggestions to return")

@tool(args_schema=StockSuggesterInput)
def suggest_stocks(risk_tolerance: RiskTolerance, investment_goal: InvestmentGoal,
                  budget: Optional[float] = None, sectors: Optional[List[str]] = None,
                  max_suggestions: int = 5) -> Dict:
    """
    Suggest stocks based on user's risk tolerance, investment goals, and preferences.
    Returns a list of recommended stocks with analysis and reasoning.
    """

    # Define stock pools based on risk tolerance
    stock_pools = {
        RiskTolerance.conservative: [
            "JNJ", "PG", "KO", "PEP", "VZ", "T", "XOM", "CVX", "WMT", "HD",
            "MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX"
        ],
        RiskTolerance.moderate: [
            "JNJ", "PG", "KO", "PEP", "VZ", "T", "XOM", "CVX", "WMT", "HD",
            "MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX",
            "AMD", "INTC", "CRM", "ORCL", "CSCO", "IBM", "ADBE", "NOW"
        ],
        RiskTolerance.aggressive: [
            "TSLA", "NVDA", "AMD", "PLTR", "SQ", "SHOP", "COIN", "RIVN",
            "LCID", "SOFI", "AFRM", "UPST", "RUN", "ENPH", "SEDG", "SPWR",
            "NIO", "XPEV", "LI", "QS", "CHPT", "BLNK", "FCEL"
        ]
    }

    selected_pool = stock_pools[risk_tolerance]

    # Filter by sectors if specified
    if sectors:
        # This is a simplified sector mapping - in production you'd want a more comprehensive mapping
        sector_mappings = {
            "technology": ["MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX", "AMD", "INTC", "CRM", "ORCL", "CSCO", "IBM", "ADBE", "NOW", "PLTR", "SQ", "SHOP"],
            "healthcare": ["JNJ"],
            "consumer": ["PG", "KO", "PEP", "WMT", "HD"],
            "energy": ["XOM", "CVX"],
            "telecom": ["VZ", "T"],
            "financial": [],  # Add more as needed
            "automotive": ["TSLA"]
        }

        filtered_stocks = []
        for sector in sectors:
            if sector.lower() in sector_mappings:
                filtered_stocks.extend(sector_mappings[sector.lower()])

        # If no stocks found in preferred sectors, fall back to full pool
        if filtered_stocks:
            selected_pool = [stock for stock in selected_pool if stock in filtered_stocks]

    # Get stock data and recommendations
    suggestions = []
    analyzed_count = 0

    for ticker in selected_pool[:max_suggestions * 2]:  # Analyze more than needed to filter
        if analyzed_count >= max_suggestions:
            break

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info:
                continue

            # Get current price and basic metrics
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            if current_price == 0:
                continue

            market_cap = info.get('marketCap', 0)
            pe_ratio = info.get('trailingPE', 0)
            dividend_yield = info.get('dividendYield', 0)
            fifty_two_week_high = info.get('fiftyTwoWeekHigh', 0)
            fifty_two_week_low = info.get('fiftyTwoWeekLow', 0)

            # Get recommendations
            try:
                recommendations = stock.recommendations_summary
                if recommendations is not None and not recommendations.empty:
                    latest_rec = recommendations.iloc[0] if len(recommendations) > 0 else None
                    if latest_rec is not None:
                        strong_buy = latest_rec.get('strongBuy', 0)
                        buy = latest_rec.get('buy', 0)
                        hold = latest_rec.get('hold', 0)
                        sell = latest_rec.get('sell', 0)
                        strong_sell = latest_rec.get('strongSell', 0)

                        total_ratings = strong_buy + buy + hold + sell + strong_sell
                        if total_ratings > 0:
                            buy_rating = (strong_buy + buy) / total_ratings
                        else:
                            buy_rating = 0
                    else:
                        buy_rating = 0
                else:
                    buy_rating = 0
            except:
                buy_rating = 0

            # Calculate score based on investment goal
            score = 0
            reasoning = []

            if investment_goal == InvestmentGoal.growth:
                # Favor high growth stocks with good analyst ratings
                if pe_ratio > 0 and pe_ratio < 50:  # Reasonable P/E for growth
                    score += 2
                    reasoning.append("Reasonable P/E ratio for growth")
                if buy_rating > 0.6:
                    score += 3
                    reasoning.append("Strong analyst buy ratings")
                if market_cap > 50000000000:  # Large cap with growth potential
                    score += 1
                    reasoning.append("Large market cap with growth potential")

            elif investment_goal == InvestmentGoal.income:
                # Favor dividend-paying stocks
                if dividend_yield > 0.02:  # >2% dividend yield
                    score += 3
                    reasoning.append("Good dividend yield for income")
                if pe_ratio > 0 and pe_ratio < 25:  # Reasonable valuation
                    score += 2
                    reasoning.append("Reasonable valuation")
                if buy_rating > 0.4:
                    score += 1
                    reasoning.append("Decent analyst ratings")

            elif investment_goal == InvestmentGoal.value:
                # Favor undervalued stocks
                current_price_ratio = (fifty_two_week_high - current_price) / (fifty_two_week_high - fifty_two_week_low) if fifty_two_week_high != fifty_two_week_low else 0
                if current_price_ratio < 0.3:  # Near 52-week low
                    score += 3
                    reasoning.append("Potentially undervalued")
                if pe_ratio > 0 and pe_ratio < 20:  # Low P/E
                    score += 2
                    reasoning.append("Low P/E ratio suggests value")
                if buy_rating > 0.5:
                    score += 1
                    reasoning.append("Positive analyst sentiment")

            else:  # balanced
                # Balanced approach
                if pe_ratio > 0 and 15 < pe_ratio < 30:
                    score += 2
                    reasoning.append("Balanced valuation")
                if buy_rating > 0.5:
                    score += 2
                    reasoning.append("Good analyst ratings")
                if dividend_yield > 0.01:
                    score += 1
                    reasoning.append("Some dividend income")

            # Budget filter
            if budget and current_price > budget:
                continue  # Skip if stock price exceeds budget

            if score >= 3:  # Only include stocks with decent scores
                suggestion = {
                    "ticker": ticker,
                    "company_name": info.get('longName', info.get('shortName', ticker)),
                    "current_price": round(current_price, 2),
                    "market_cap": market_cap,
                    "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
                    "dividend_yield": round(dividend_yield * 100, 2) if dividend_yield else None,
                    "analyst_buy_rating": round(buy_rating * 100, 1) if buy_rating else None,
                    "score": score,
                    "reasoning": reasoning,
                    "sector": info.get('sector', 'Unknown'),
                    "industry": info.get('industry', 'Unknown')
                }
                suggestions.append(suggestion)
                analyzed_count += 1

        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            continue

    # Sort by score (highest first)
    suggestions.sort(key=lambda x: x['score'], reverse=True)

    # Return top suggestions
    result = {
        "risk_tolerance": risk_tolerance,
        "investment_goal": investment_goal,
        "budget": budget,
        "preferred_sectors": sectors,
        "suggestions": suggestions[:max_suggestions],
        "total_analyzed": len(suggestions)
    }

    return result