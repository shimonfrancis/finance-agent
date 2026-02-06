from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import yfinance as yf
from llm.llm import llm
from enum import Enum

class AnalysisType(str, Enum):
    comprehensive = "comprehensive"
    quick = "quick"
    risk_focused = "risk_focused"
    news_driven = "news_driven"

class StockAnalyserInput(BaseModel):
    ticker: str = Field(..., description="The ticker symbol to analyze")
    analysis_type: AnalysisType = Field(AnalysisType.comprehensive, description="Type of analysis to perform")
    news_sentiment: Optional[float] = Field(None, description="News sentiment score from news agent")
    key_news_takeaways: Optional[List[str]] = Field(None, description="Key news takeaways from news agent")
    risk_tolerance: Optional[str] = Field(None, description="User's risk tolerance (conservative/moderate/aggressive)")

@tool(args_schema=StockAnalyserInput)
def analyze_stock_comprehensive(ticker: str, analysis_type: AnalysisType = AnalysisType.comprehensive,
                               news_sentiment: Optional[float] = None,
                               key_news_takeaways: Optional[List[str]] = None,
                               risk_tolerance: Optional[str] = None) -> Dict:
    """
    Perform comprehensive stock analysis combining financial data, news sentiment, and investment rules.
    Provides detailed analysis with buy/hold/sell recommendations and risk assessment.
    """

    try:
        # Get financial data
        stock = yf.Ticker(f'{ticker}.NS')
        info = stock.info

        if not info:
            return {"error": f"Unable to fetch data for {ticker}"}

        # Extract key financial metrics
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        market_cap = info.get('marketCap', 0)
        pe_ratio = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        dividend_yield = info.get('dividendYield', 0)
        beta = info.get('beta', 1.0)
        fifty_two_week_high = info.get('fiftyTwoWeekHigh', 0)
        fifty_two_week_low = info.get('fiftyTwoWeekLow', 0)
        volume = info.get('volume', 0)
        avg_volume = info.get('averageVolume', 0)

        # Get analyst recommendations
        try:
            recommendations = stock.recommendations_summary
            analyst_rating = "N/A"
            if recommendations is not None and not recommendations.empty:
                latest_rec = recommendations.iloc[0]
                strong_buy = latest_rec.get('strongBuy', 0)
                buy = latest_rec.get('buy', 0)
                hold = latest_rec.get('hold', 0)
                sell = latest_rec.get('sell', 0)
                total = strong_buy + buy + hold + sell
                if total > 0:
                    buy_percentage = (strong_buy + buy) / total
                    if buy_percentage > 0.7:
                        analyst_rating = "Strong Buy"
                    elif buy_percentage > 0.5:
                        analyst_rating = "Buy"
                    elif buy_percentage > 0.3:
                        analyst_rating = "Hold"
                    else:
                        analyst_rating = "Sell"
        except:
            analyst_rating = "N/A"

        # Calculate technical indicators
        price_to_52w_high = (current_price / fifty_two_week_high) if fifty_two_week_high > 0 else 0
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1

        # Prepare analysis context
        financial_data = {
            "current_price": current_price,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "forward_pe": forward_pe,
            "dividend_yield": dividend_yield * 100 if dividend_yield else 0,
            "beta": beta,
            "price_to_52w_high": price_to_52w_high,
            "volume_ratio": volume_ratio,
            "analyst_rating": analyst_rating
        }

        # Prepare news context
        news_context = ""
        if news_sentiment is not None:
            sentiment_desc = "positive" if news_sentiment > 0.1 else "negative" if news_sentiment < -0.1 else "neutral"
            news_context = f"Recent news sentiment is {sentiment_desc} (score: {news_sentiment:.2f}). "

        if key_news_takeaways:
            news_context += f"Key news takeaways: {'; '.join(key_news_takeaways[:3])}"

        # Create analysis prompt based on type
        if analysis_type == AnalysisType.comprehensive:
            prompt = f"""
            Perform a comprehensive analysis of {ticker} stock. Consider:

            FINANCIAL DATA:
            - Current Price: ${current_price}
            - Market Cap: {market_cap:,}
            - P/E Ratio: {pe_ratio}
            - Forward P/E: {forward_pe}
            - Dividend Yield: {financial_data['dividend_yield']}%
            - Beta: {beta}
            - Analyst Rating: {analyst_rating}
            - Price vs 52W High: {price_to_52w_high:.1%}
            - Volume Ratio: {volume_ratio:.2f}

            NEWS CONTEXT:
            {news_context}

            RISK TOLERANCE: {risk_tolerance or 'Not specified'}

            Provide:
            1. Overall investment recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
            2. Key strengths and opportunities
            3. Key risks and concerns
            4. Valuation assessment (Undervalued/Fairly Valued/Overvalued)
            5. Risk level assessment (Low/Moderate/High/Very High)
            6. Investment timeframe recommendation
            7. Key catalysts to watch
            """

        elif analysis_type == AnalysisType.quick:
            prompt = f"Provide a quick analysis and rating for {ticker} stock based on key metrics and news sentiment."

        elif analysis_type == AnalysisType.risk_focused:
            prompt = f"Focus on risk analysis for {ticker}. Assess volatility, downside potential, and risk-adjusted return potential."

        else:  # news_driven
            prompt = f"Analyze {ticker} primarily based on recent news and sentiment. How might news impact the stock?"

        # Get AI analysis
        try:
            response = llm.invoke(prompt)
            analysis_text = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            analysis_text = f"Error in AI analysis: {str(e)}"

        # Generate recommendation score (simplified)
        recommendation_score = 0

        # Financial factors
        if pe_ratio > 0 and pe_ratio < 25:
            recommendation_score += 1  # Reasonable valuation
        if dividend_yield and dividend_yield > 0.02:
            recommendation_score += 1  # Good dividend
        if beta < 1.2:
            recommendation_score += 1  # Reasonable volatility
        if analyst_rating in ["Strong Buy", "Buy"]:
            recommendation_score += 2  # Positive analyst sentiment

        # News sentiment factor
        if news_sentiment:
            recommendation_score += news_sentiment * 2  # Scale news sentiment

        # Risk tolerance adjustment
        if risk_tolerance == "conservative" and beta > 1.5:
            recommendation_score -= 1  # Too volatile for conservative investors
        elif risk_tolerance == "aggressive" and beta < 0.8:
            recommendation_score -= 0.5  # Too stable for aggressive investors

        # Convert to recommendation
        if recommendation_score >= 3:
            final_recommendation = "Buy"
        elif recommendation_score >= 1:
            final_recommendation = "Hold"
        elif recommendation_score >= -1:
            final_recommendation = "Hold"
        else:
            final_recommendation = "Sell"

        return {
            "ticker": ticker,
            "company_name": info.get('longName', ticker),
            "analysis_type": analysis_type,
            "financial_data": financial_data,
            "news_sentiment": news_sentiment,
            "key_news_takeaways": key_news_takeaways or [],
            "ai_analysis": analysis_text,
            "recommendation_score": recommendation_score,
            "final_recommendation": final_recommendation,
            "risk_tolerance_considered": risk_tolerance,
            "analysis_timestamp": "2024-01-24"  # Would be datetime.now() in production
        }

    except Exception as e:
        return {
            "error": f"Analysis failed for {ticker}: {str(e)}",
            "ticker": ticker
        }

# Additional helper functions
def compare_stocks(tickers: List[str], analysis_type: AnalysisType = AnalysisType.quick) -> Dict:
    """Compare multiple stocks side by side"""
    results = {}
    for ticker in tickers:
        results[ticker] = analyze_stock_comprehensive(ticker, analysis_type)

    return {
        "comparison": results,
        "tickers_compared": tickers,
        "analysis_type": analysis_type
    }

def get_sector_analysis(ticker: str) -> Dict:
    """Analyze stock in context of its sector"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        sector = info.get('sector', 'Unknown')

        # This would typically query sector peers and comparables
        # For now, return basic sector context
        return {
            "ticker": ticker,
            "sector": sector,
            "industry": info.get('industry', 'Unknown'),
            "sector_peers": ["Sample peer 1", "Sample peer 2"],  # Would be actual peers
            "sector_average_pe": 20.5,  # Would be calculated
            "relative_valuation": "Fair"  # Would be calculated
        }
    except Exception as e:
        return {"error": str(e)}