# Stock Suggester Agent

A comprehensive AI-powered stock recommendation system built with LangChain, LangGraph, and financial data APIs.

## Features

### 🎯 Intelligent Stock Recommendations
- **Risk-Based Selection**: Conservative, Moderate, and Aggressive investment profiles
- **Goal-Oriented Suggestions**: Growth, Income, Value, and Balanced investment strategies
- **Budget-Aware Filtering**: Respects investment budget constraints
- **Multi-Factor Analysis**: P/E ratios, dividend yields, analyst ratings, market cap

### 🛠️ Available Tools
- **Stock Information** (`get_stock_info`): Real-time price, market cap, fundamentals
- **Analyst Recommendations** (`get_recommendations`): Buy/sell ratings and summaries
- **Company Search** (`list_companies`): Search companies from CSV database
- **Options Data** (`get_options`, `get_option_chain`): Options analysis
- **Financial Actions** (`get_actions`): Dividends, splits, corporate actions

### 🤖 AI Agent Framework
- **Conversational Interface**: Natural language stock recommendations
- **Tool Integration**: Automatic tool calling for data retrieval
- **Reasoned Responses**: Detailed explanations for each recommendation

## Project Structure

```
├── main.py                 # Main application entry point
├── graph/                  # LangGraph agent implementation
│   └── graph.py           # Stock suggester agent workflow
├── tools/                  # Financial analysis tools
│   ├── stock_suggester.py # Core recommendation engine
│   ├── get_stock_info.py  # Stock data retrieval
│   ├── get_recommendations.py # Analyst ratings
│   ├── list_companies.py  # Company search
│   └── ...                # Additional financial tools
├── llm/                    # Language model configuration
├── Companies.csv          # Company database
├── mock_stock_suggester.py # Demo with sample data
├── simple_stock_suggester.py # Standalone version
└── requirements.txt       # Python dependencies
```

## Usage

### Quick Demo (Mock Data)
```bash
python main.py
```
Shows example recommendations for different investor profiles using sample data.

### Real Data Version
```bash
python simple_stock_suggester.py
```
Requires network access to Yahoo Finance API.

### Interactive Agent (Full LangChain)
```python
from graph.graph import app
from langchain_core.messages import HumanMessage

result = app.invoke({
    "messages": [HumanMessage(content="I'm conservative with $5000, suggest income stocks")]
})
print(result["messages"][-1].content)
```

## Investment Profiles

### Risk Tolerance
- **Conservative**: Blue-chip stocks, stable companies, dividend payers
- **Moderate**: Balanced mix of stable and growth stocks
- **Aggressive**: High-growth tech, innovative companies, higher volatility

### Investment Goals
- **Growth**: Focus on capital appreciation, higher P/E stocks
- **Income**: Dividend-paying stocks with steady yields
- **Value**: Undervalued stocks with low P/E ratios
- **Balanced**: Mix of growth and income characteristics

## Scoring Algorithm

Each stock receives a score (0-6) based on:
- **Growth Focus**: P/E ratio appropriateness, analyst ratings, market cap
- **Income Focus**: Dividend yield (>2%), valuation, analyst sentiment
- **Value Focus**: Low P/E ratios, analyst ratings
- **Balanced**: Moderate valuations, good ratings, some dividends

## Dependencies

- `yfinance`: Yahoo Finance API access
- `pandas`: Data manipulation
- `langchain-core`: Core LangChain functionality
- `langgraph`: Agent workflow management
- `chromadb`: Vector database for company search

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
# or
uv sync

# Run demo
python main.py
```

## Example Output

```
STOCK SUGGESTIONS
Risk Tolerance: Conservative
Investment Goal: Income
Budget: $10,000
============================================================

1. JNJ - Johnson & Johnson
   Current Price: $165.80
   Sector: Healthcare
   P/E Ratio: 18.2
   Dividend Yield: 3.2%
   Analyst Buy Rating: 65.0%
   Score: 6/6
   Reasoning:
   • Good dividend yield for income
   • Reasonable valuation
   • Decent analyst ratings
```

## Future Enhancements

- Real-time market data integration
- Portfolio optimization algorithms
- Risk assessment models
- Historical performance analysis
- Sector rotation strategies
- ESG (Environmental, Social, Governance) filtering

## Disclaimer

This is a demonstration system for educational purposes. Not intended as financial advice. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.