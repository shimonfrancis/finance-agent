from typing import TypedDict, List, Literal, Optional, Dict, Any,Annotated
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from llm.llm import llm
from tools import (companies_list, analyze_stock_news,
                   query_investment_rules, analyze_stock_comprehensive,get_financials,get_historical_data,get_recommendations)
from tools.stock_suggester import suggest_stocks
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from tools.technical_analysis import calculate_technicals
from langgraph.checkpoint.memory import InMemorySaver
from utils.logger import logger


def overwrite_reducer(left: str, right: str) -> str:
    return right

# Define extended state for multi-agent workflow
class MultiAgentState(TypedDict):
    messages: List[HumanMessage | AIMessage | ToolMessage | SystemMessage]
    selected_companies: List[str]
    news_analysis: Dict[str, Any]
    rules_guidance: Dict[str, Any]
    stock_analysis: Dict[str, Any]
    final_recommendations: Dict[str, Any]
    current_agent: Annotated[str, overwrite_reducer]

# Bind tools for each agent
companies_llm = llm.bind_tools([companies_list])
news_llm = llm.bind_tools([analyze_stock_news])
rules_llm = llm.bind_tools([query_investment_rules])
analyser_llm = llm.bind_tools([analyze_stock_comprehensive])
suggester_llm = llm.bind_tools([suggest_stocks])
research_agent=llm.bind_tools([get_financials,get_historical_data,get_recommendations])

def companies_list_agent(state: MultiAgentState) -> Dict:
    """Agent that searches for relevant companies based on user query"""

    messages = state.get("messages", [])
    logger.info("companies_list_agent called")
    logger.debug(f"Input messages: {messages}")
    print(messages)

    # Add system message for company search
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        system_msg = SystemMessage(content="""
        You are a company research specialist. Your role is to:

        1. Understand what companies the user is interested in
        2. Search the companies database for relevant matches
        3. Return a focused list of 3-5 ticker symbols for further analysis

        Focus on well-known, liquid stocks that are suitable for investment analysis.
        Prioritize companies based on market relevance and investment interest.
        """)
        messages = [system_msg] + messages

    # Get response from LLM
    response = companies_llm.invoke(messages)

    # Check for tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_messages = []
        for tool_call in response.tool_calls:
            if tool_call['name'] == 'companies_list':
                result = companies_list.invoke(tool_call['args'])
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call['id']))

                # Extract tickers from the result (simplified parsing)
                # In production, you'd want more robust parsing
                result_str = str(result)
                # Look for common tickers in the response
                import re
                exclude_list = {'SYMBOL', 'EQ', 'NAME', 'COMPANY', 'SERIES', 'DATE', 'LISTING', 'PAID', 'MARKET', 'LOT', 'ISIN', 'FACE', 'VALUE'}
                potential_tickers = re.findall(r'\b[A-Z][A-Z0-9-]{1,11}\b', result_str)
                selected_companies = [t for t in potential_tickers if t not in exclude_list]
                selected_companies = list(set(selected_companies)) # Limit to 5

        return {
            "messages": [response] + tool_messages,
            "selected_companies": selected_companies,
            "current_agent": "news_agent"
        }

    return {
        "messages": [response],
        "current_agent": "news_agent"
    }

def news_agent(state: MultiAgentState) -> Dict:
    """Agent that analyzes news for selected companies"""

    selected_companies = state.get("selected_companies", [])
    logger.info(f"news_agent called with {len(selected_companies)} companies")
    logger.debug(f"Companies: {selected_companies}")
    print(selected_companies)

    if not selected_companies:
        return {
            "news_analysis": {"error": "No companies selected"},
            "current_agent": "stock_analyser_agent"
        }

    # Create news analysis request
    news_request = {
        "tickers": selected_companies,
        "max_articles_per_ticker": 3
    }

    result = analyze_stock_news.invoke(news_request)

    return {
        "news_analysis": result,
        "current_agent": "stock_analyser_agent"
    }

def rules_rag_agent(state: MultiAgentState) -> Dict:
    """Agent that provides investment rules and regulatory guidance"""

    messages = state.get("messages", [])
    logger.info("rules_rag_agent called")
    logger.debug(f"Input messages: {messages}")

    # Extract user preferences from messages
    user_query = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            user_query = msg.content
            break

    # Query rules based on user query
    rules_result = query_investment_rules.invoke({
        "query": f"Provide investment guidance and rules relevant to: {user_query}",
        "context": "User is seeking stock investment advice"
    })

    return {
        "rules_guidance": rules_result,
        "current_agent": "stock_analyser_agent"
    }

def researcher_agent(state: MultiAgentState) -> Dict:
    """
    Performs DEEP TECHNICAL research.
    Instead of just fetching data, this agent calculates indicators (RSI, MACD)
    to find actual trade setups.
    """
    selected_companies = state.get("selected_companies", [])
    logger.info(f"researcher_agent called with {len(selected_companies)} companies")
    logger.debug(f"Companies: {selected_companies}")
    if not selected_companies:
        return {"current_agent": "suggester_agent"}

    research_output = {}
    
    for ticker in selected_companies:
        print(f"Analyzing Technicals for {ticker}...")
        
        # 1. Fetch enough data for indicators (need >26 days for MACD)
        # We request '2mo' to ensure we have enough data points for smooth Moving Averages
        historical_raw = get_historical_data.invoke({"ticker": ticker, "period": "3mo"})
        
        # 2. RUN TECHNICAL ANALYSIS (The Math Brain)
        # This function (imported from technical_tools) calculates RSI, MACD, BB, etc.
        tech_signals = calculate_technicals(historical_raw)
        
        # 3. Get News Context (already fetched or fetch brief)
        # We use the previous agent's news, or fetch fresh if empty
        
        research_output[ticker] = {
            "technical_signals": tech_signals,
            "raw_data_summary": "Processed 3 months of OHLCV data"
        }

    return {
        "stock_analysis": research_output,
        "current_agent": "stock_analyser_agent"
    }


def stock_analyser_agent(state: MultiAgentState) -> Dict:
    """Agent that combines news, rules, and financial data for analysis"""

    selected_companies = state.get("selected_companies", [])
    news_analysis = state.get("news_analysis", {})
    rules_guidance = state.get("rules_guidance", {})
    messages = state.get("messages", [])
    logger.info(f"stock_analyser_agent called with {len(selected_companies)} companies")
    logger.debug(f"Companies: {selected_companies}")

    # Extract risk tolerance from user query
    risk_tolerance = "moderate"  # default
    user_query = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            user_query = msg.content.lower()
            if "conservative" in user_query:
                risk_tolerance = "conservative"
            elif "aggressive" in user_query:
                risk_tolerance = "aggressive"
            break

    analysis_results = {}

    # Analyze each selected company
    for ticker in selected_companies:  # Limit to top 3
        # Get news sentiment for this ticker
        ticker_news = news_analysis.get("news_analysis", {}).get(ticker, {})
        news_sentiment = ticker_news.get("sentiment_score", 0)
        key_takeaways = ticker_news.get("key_takeaways", [])

        # Analyze the stock
        stock_analysis = analyze_stock_comprehensive.invoke({
            "ticker": ticker,
            "analysis_type": "comprehensive",
            "news_sentiment": news_sentiment,
            "key_news_takeaways": key_takeaways,
            "risk_tolerance": risk_tolerance
        })

        analysis_results[ticker] = stock_analysis

    return {
        "stock_analysis": analysis_results,
        "current_agent": "suggester"
    }

def suggester_agent(state: MultiAgentState) -> Dict:
    """
    The 'Senior Trader' agent that combines news, rules, and financial data for analysis.
    It takes the calculated technical signals and formulates a specific trade plan.
    """
    selected_companies = state.get("selected_companies", [])
    news_analysis = state.get("news_analysis", {})
    rules_guidance = state.get("rules_guidance", {})
    messages = state.get("messages", [])
    
    # ✅ GET EXISTING TECHNICAL DATA FROM RESEARCHER
    existing_analysis = state.get("stock_analysis", {})
    
    logger.info(f"stock_analyser_agent called with {len(selected_companies)} companies")
    logger.debug(f"Companies: {selected_companies}")
    
    risk_tolerance = "moderate"
    user_query = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            user_query = msg.content.lower()
            if "conservative" in user_query:
                risk_tolerance = "conservative"
            elif "aggressive" in user_query:
                risk_tolerance = "aggressive"
            break
    analysis_results = {}
    for ticker in selected_companies:
        ticker_news = news_analysis.get("news_analysis", {}).get(ticker, {})
        news_sentiment = ticker_news.get("sentiment_score", 0)
        key_takeaways = ticker_news.get("key_takeaways", [])
        stock_analysis = analyze_stock_comprehensive.invoke({
            "ticker": ticker,
            "analysis_type": "comprehensive",
            "news_sentiment": news_sentiment,
            "key_news_takeaways": key_takeaways,
            "risk_tolerance": risk_tolerance
        })
        # ✅ MERGE: Keep technical_signals from researcher + add new financial data
        analysis_results[ticker] = {
            **stock_analysis,  # financial_data, ai_analysis, etc.
            "technical_signals": existing_analysis.get(ticker, {}).get("technical_signals", {})
        }
    return {
        "stock_analysis": analysis_results,
        "current_agent": "suggester"
    }
# Create the multi-agent workflow
workflow = StateGraph[MultiAgentState, None, MultiAgentState, MultiAgentState](MultiAgentState)

# Add all agent nodes
workflow.add_node("companies_list_agent", companies_list_agent)
workflow.add_node("news_agent", news_agent)
workflow.add_node("rules_rag_agent", rules_rag_agent)
workflow.add_node("researcher_agent", researcher_agent)
workflow.add_node("suggester_agent", suggester_agent)
workflow.add_node("stock_analyser_agent", stock_analyser_agent)




# Define the workflow: companies -> news -> rules -> research -> suggester
# 1. Start with companies list agent as entry point
workflow.set_entry_point("companies_list_agent")

# Companies -> News
workflow.add_edge("companies_list_agent", "news_agent")

# News -> Rules RAG (get trading rules before research)
workflow.add_edge("news_agent", "rules_rag_agent")

# Rules RAG -> Researcher (deep dive with rules context)
workflow.add_edge("rules_rag_agent", "researcher_agent")

workflow.add_edge("researcher_agent", "stock_analyser_agent")

# Researcher -> Suggester (final trade plan)
workflow.add_edge("stock_analyser_agent", "suggester_agent")

# 3. Finish
workflow.set_finish_point("suggester_agent")
checkpointer=InMemorySaver()

# Compile the graph
app = workflow.compile(checkpointer=checkpointer)
