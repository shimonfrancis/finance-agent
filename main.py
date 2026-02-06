"""
Multi-Agent Stock Analysis System

This application demonstrates a sophisticated multi-agent stock analysis system
that follows the architecture shown in the Excalidraw diagram:

Companies List Agent → News Agent → Stock Analyser Agent → Suggester
                         ↑
                    Rules RAG Agent

The workflow:
1. Companies List Agent: Searches for relevant companies based on user criteria
2. News Agent: Analyzes recent news and sentiment for selected companies
3. Rules RAG Agent: Provides investment rules and regulatory guidance
4. Stock Analyser Agent: Combines financial data, news, and rules for deep analysis
5. Suggester: Provides final investment recommendations

Available Tools:
- Company search and filtering
- News sentiment analysis
- Investment rules and regulations
- Comprehensive stock analysis
- Personalized recommendations
"""

from graph.graph import app
from langchain_core.messages import HumanMessage
app.get_graph().draw_mermaid_png(output_file_path=r'C:\Users\shimo\Desktop\Imp_Scripts\Reasearch_Agent\graph.png')

def run_day_trading_session(user_query: str, session_name: str = ""):
    """Run the AI Day Trader workflow"""
    print(f"\n{'='*60}")
    print(f"SESSION: {session_name}")
    print(f"STRATEGY: {user_query}")
    print(f"{'='*60}")

    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "selected_companies": [],
        "news_analysis": {},
        "rules_guidance": {},
        "stock_analysis": {},  # This will now contain Technical Signals
        "final_recommendations": {},
        "current_agent": "rules_rag_agent" # Start with Rules/Strategy
    }

    try:
        # Run the Graph
        result = app.invoke(initial_state,config={"configurable": {"thread_id": "monitor-session"}})

        print("\n>>> TRADING SESSION COMPLETE <<<")
        print("-" * 40)

        # 1. Print the Final Trade Plan
        for message in result["messages"]:
            if hasattr(message, 'content') and message.content.strip():
                # We expect the final message to be the Trade Plan
                print(message.content)

        # 2. Print Debug/Process Info (Optional but helpful for trust)
        if result.get("selected_companies"):
            print(f"\n[Scanner] Tickers Identified: {', '.join(result['selected_companies'])}")

        if result.get("stock_analysis"):
            print(f"[Technicals] Analyzed Indicators for {len(result['stock_analysis'])} stocks")

    except Exception as e:
        print(f"Error in trading session: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("AI ALGORITHMIC DAY TRADER")
    print("=" * 50)
    print("Modules Loaded:")
    print("1. Market Scanner (Volume/Volatility)")
    print("2. Technical Engine (RSI, MACD, BB, EMA)")
    print("3. Risk Manager (Stop Loss Calculation)")
    
    # Scenario 1: Momentum Trading (The most common day trading strategy)
    run_day_trading_session(
        """Find high momentum stocks suitable for intraday breakout trading. Look for volume spikes.
        Find stocks that are overbought (RSI > 70) or oversold (RSI < 30) for a mean reversion trade.
        Identify stocks reacting to recent news or earnings for a quick scalp."""
    )

    # Scenario 2: Reversal Trading (Buying the dip or Shorting the top)
    # run_day_trading_session(
    #     "Find stocks that are overbought (RSI > 70) or oversold (RSI < 30) for a mean reversion trade.",
    #     "Scenario 2: Mean Reversion"
    # )

    # Scenario 3: News Based
    # run_day_trading_session(
    #     "Identify stocks reacting to recent news or earnings for a quick scalp.",
    #     "Scenario 3: News Catalyst"
    # )

    print(f"\n{'='*60}")
    print("DISCLAIMER: AI suggestions are based on technical patterns.")
    print("Always verify with your own charts before executing real trades.")