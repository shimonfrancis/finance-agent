from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import yfinance as yf
from llm.llm import llm

class NewsAgentInput(BaseModel):
    tickers: List[str] = Field(..., description="List of ticker symbols to analyze news for")
    max_articles_per_ticker: int = Field(5, description="Maximum number of articles to analyze per ticker")

@tool(args_schema=NewsAgentInput)
def analyze_stock_news(tickers: List[str], max_articles_per_ticker: int = 5) -> Dict:
    """
    Analyze recent news for given stock tickers and provide sentiment analysis and key insights.
    Returns summarized news analysis with sentiment scores and key takeaways.
    """

    analysis_results = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            news = stock.news

            if not news:
                analysis_results[ticker] = {
                    "error": f"No news available for {ticker}",
                    "sentiment_score": 0,
                    "key_takeaways": [],
                    "article_count": 0
                }
                continue

            # Limit articles per ticker
            articles_to_analyze = news[:max_articles_per_ticker]

            # Extract titles and summaries
            article_summaries = []
            for article in articles_to_analyze:
                title = article.get('title', '')
                summary = article.get('summary', '')
                publisher = article.get('publisher', '')
                link = article.get('link', '')

                article_summaries.append({
                    'title': title,
                    'summary': summary,
                    'publisher': publisher,
                    'link': link
                })

            # Use LLM to analyze sentiment and extract key insights
            news_text = "\n\n".join([
                f"Title: {article['title']}\nSummary: {article['summary']}"
                for article in article_summaries
            ])

            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following news articles for {ticker} and provide:

            1. Overall sentiment score (-1 to 1, where -1 is very negative, 0 is neutral, 1 is very positive)
            2. Key positive developments or news
            3. Key negative developments or concerns
            4. Risk factors mentioned
            5. Overall market impact assessment

            News articles:
            {news_text}

            Provide your analysis in a structured format.
            """

            # Get LLM analysis
            try:
                response = llm.invoke(analysis_prompt)
                llm_analysis = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                llm_analysis = f"Error in LLM analysis: {str(e)}"

            # Simple sentiment scoring based on keywords (fallback if LLM fails)
            positive_keywords = ['rise', 'gain', 'increase', 'growth', 'profit', 'beat', 'surge', 'rally', 'upgrade', 'buy', 'bullish', 'positive']
            negative_keywords = ['fall', 'drop', 'decrease', 'loss', 'decline', 'miss', 'plunge', 'crash', 'downgrade', 'sell', 'bearish', 'negative', 'concern', 'worry']

            all_text = " ".join([article['title'] + " " + article['summary'] for article in article_summaries]).lower()

            positive_count = sum(1 for word in positive_keywords if word in all_text)
            negative_count = sum(1 for word in negative_keywords if word in all_text)

            # Calculate simple sentiment score
            total_sentiment_words = positive_count + negative_count
            if total_sentiment_words > 0:
                simple_sentiment = (positive_count - negative_count) / total_sentiment_words
            else:
                simple_sentiment = 0

            # Extract key takeaways from article titles
            key_takeaways = [article['title'] for article in article_summaries[:3]]  # Top 3 headlines

            analysis_results[ticker] = {
                "sentiment_score": simple_sentiment,
                "llm_analysis": llm_analysis,
                "key_takeaways": key_takeaways,
                "article_count": len(articles_to_analyze),
                "recent_articles": article_summaries,
                "positive_signals": positive_count,
                "negative_signals": negative_count
            }

        except Exception as e:
            analysis_results[ticker] = {
                "error": f"Error analyzing news for {ticker}: {str(e)}",
                "sentiment_score": 0,
                "key_takeaways": [],
                "article_count": 0
            }

    return {
        "news_analysis": analysis_results,
        "tickers_analyzed": len(tickers),
        "total_articles": sum(result.get("article_count", 0) for result in analysis_results.values())
    }