#!/usr/bin/env python3
"""
Multi-Agent Stock Analysis Demo

This demonstrates the multi-agent workflow architecture from the Excalidraw diagram:
Companies List Agent -> News Agent -> Stock Analyser Agent -> Suggester
                         |
                    Rules RAG Agent

Since full LangChain dependencies aren't available, this simulates the workflow
with mock data to show how the multi-agent system would work.
"""

from typing import List, Dict, Any
from mock_stock_suggester import RiskTolerance, InvestmentGoal

class MultiAgentWorkflow:
    """Simulates the multi-agent workflow"""

    def __init__(self):
        self.workflow_state = {
            "companies": [],
            "news_analysis": {},
            "rules_guidance": {},
            "stock_analysis": {},
            "final_recommendations": {}
        }

    def companies_list_agent(self, user_query: str) -> List[str]:
        """Simulate company search agent"""
        print("[COMPANIES] Companies List Agent: Searching for relevant companies...")

        # Mock company selection based on query
        if "tech" in user_query.lower() or "technology" in user_query.lower():
            companies = ["AAPL", "MSFT", "NVDA", "AMD"]
        elif "dividend" in user_query.lower() or "income" in user_query.lower():
            companies = ["JNJ", "PG", "KO", "XOM"]
        else:
            companies = ["AAPL", "MSFT", "JNJ", "KO"]

        self.workflow_state["companies"] = companies
        print(f"   Selected companies: {', '.join(companies)}")
        return companies

    def news_agent(self, companies: List[str]) -> Dict[str, Any]:
        """Simulate news analysis agent"""
        print("[NEWS] News Agent: Analyzing recent news and sentiment...")

        # Mock news analysis
        news_analysis = {
            "total_articles": len(companies) * 3,
            "companies_analyzed": len(companies),
            "sentiment_summary": "Mixed sentiment with some positive developments",
            "key_themes": ["earnings reports", "market performance", "industry trends"]
        }

        for company in companies[:2]:  # Analyze top 2 for demo
            news_analysis[company] = {
                "sentiment_score": 0.3 if company in ["AAPL", "MSFT"] else -0.1,
                "articles_analyzed": 3,
                "key_takeaways": [
                    f"{company} reported Q4 earnings",
                    f"Market reactions mixed for {company}",
                    f"Industry analysts comment on {company} performance"
                ]
            }

        self.workflow_state["news_analysis"] = news_analysis
        print(f"   Analyzed {news_analysis['total_articles']} articles")
        print("   Overall sentiment: Mixed with positive bias")
        return news_analysis

    def rules_rag_agent(self, user_query: str) -> Dict[str, Any]:
        """Simulate rules and regulations agent"""
        print("[RULES] Rules RAG Agent: Applying investment rules and regulations...")

        # Mock rules guidance
        rules_guidance = {
            "relevant_rules": [
                "Diversification Principle",
                "Risk tolerance assessment",
                "Long-term investing focus"
            ],
            "categories": ["Risk Management", "Portfolio Management"],
            "key_guidance": [
                "Maintain proper diversification across assets",
                "Match investments to risk tolerance",
                "Consider long-term holding periods"
            ],
            "compliance_notes": [
                "Follow SEC guidelines for investment recommendations",
                "Consider fiduciary duty requirements"
            ]
        }

        self.workflow_state["rules_guidance"] = rules_guidance
        print(f"   Applied {len(rules_guidance['relevant_rules'])} investment rules")
        return rules_guidance

    def stock_analyser_agent(self, companies: List[str], news_analysis: Dict,
                           rules_guidance: Dict, user_query: str) -> Dict[str, Any]:
        """Simulate comprehensive stock analysis agent"""
        print("[ANALYSER] Stock Analyser Agent: Performing deep financial analysis...")

        # Extract user preferences
        risk_tolerance = RiskTolerance.moderate
        investment_goal = InvestmentGoal.balanced

        if "conservative" in user_query.lower():
            risk_tolerance = RiskTolerance.conservative
        elif "aggressive" in user_query.lower():
            risk_tolerance = RiskTolerance.aggressive

        if "growth" in user_query.lower():
            investment_goal = InvestmentGoal.growth
        elif "income" in user_query.lower():
            investment_goal = InvestmentGoal.income

        # Mock analysis for each company
        analysis_results = {}
        for company in companies[:3]:  # Analyze top 3
            # Get news sentiment
            news_sentiment = news_analysis.get(company, {}).get("sentiment_score", 0)

            analysis_results[company] = {
                "ticker": company,
                "recommendation": "Buy" if news_sentiment > 0 else "Hold",
                "confidence": "Medium",
                "key_factors": [
                    f"News sentiment: {'Positive' if news_sentiment > 0 else 'Neutral'}",
                    "Financial metrics within acceptable range",
                    f"Risk tolerance match: {risk_tolerance.title()}"
                ],
                "risk_assessment": "Moderate" if risk_tolerance == RiskTolerance.moderate else
                                 "Low" if risk_tolerance == RiskTolerance.conservative else "High",
                "investment_timeframe": "Long-term" if investment_goal != InvestmentGoal.growth else "Medium-term"
            }

        self.workflow_state["stock_analysis"] = analysis_results
        print(f"   Analyzed {len(analysis_results)} companies comprehensively")
        return analysis_results

    def suggester_agent(self, stock_analysis: Dict, rules_guidance: Dict,
                       user_query: str) -> Dict[str, Any]:
        """Simulate final recommendation agent"""
        print("[SUGGESTER] Suggester Agent: Generating personalized recommendations...")

        # Extract user preferences
        risk_tolerance = RiskTolerance.moderate
        investment_goal = InvestmentGoal.balanced
        budget = 10000

        if "conservative" in user_query.lower():
            risk_tolerance = RiskTolerance.conservative
        elif "aggressive" in user_query.lower():
            risk_tolerance = RiskTolerance.aggressive

        if "growth" in user_query.lower():
            investment_goal = InvestmentGoal.growth
        elif "income" in user_query.lower():
            investment_goal = InvestmentGoal.income

        # Generate final recommendations
        recommendations = []
        for ticker, analysis in stock_analysis.items():
            if analysis["recommendation"] in ["Buy", "Strong Buy"]:
                recommendations.append({
                    "ticker": ticker,
                    "recommendation": analysis["recommendation"],
                    "confidence": analysis["confidence"],
                    "rationale": "; ".join(analysis["key_factors"])
                })

        final_recommendations = {
            "user_profile": {
                "risk_tolerance": risk_tolerance,
                "investment_goal": investment_goal,
                "budget": budget
            },
            "recommendations": recommendations[:3],  # Top 3
            "applied_rules": rules_guidance["relevant_rules"],
            "disclaimer": "This is educational analysis, not financial advice"
        }

        self.workflow_state["final_recommendations"] = final_recommendations
        print(f"   Generated {len(recommendations)} recommendations")
        return final_recommendations

    def run_workflow(self, user_query: str) -> Dict[str, Any]:
        """Execute the complete multi-agent workflow"""
        print(f"\n{'='*70}")
        print(f"Multi-Agent Analysis Workflow")
        print(f"Query: {user_query}")
        print(f"{'='*70}")

        # Step 1: Company selection
        companies = self.companies_list_agent(user_query)

        # Step 2: News analysis (parallel with rules)
        news_analysis = self.news_agent(companies)

        # Step 3: Rules guidance
        rules_guidance = self.rules_rag_agent(user_query)

        # Step 4: Stock analysis (combines news + rules)
        stock_analysis = self.stock_analyser_agent(companies, news_analysis,
                                                 rules_guidance, user_query)

        # Step 5: Final recommendations
        final_recommendations = self.suggester_agent(stock_analysis, rules_guidance, user_query)

        return self.workflow_state

def print_workflow_results(results: Dict[str, Any]):
    """Print formatted workflow results"""
    print(f"\n{'='*70}")
    print("WORKFLOW RESULTS SUMMARY")
    print(f"{'='*70}")

    # User profile
    profile = results["final_recommendations"]["user_profile"]
    print(f"[PROFILE] User Profile:")
    print(f"   Risk Tolerance: {profile['risk_tolerance'].title()}")
    print(f"   Investment Goal: {profile['investment_goal'].title()}")
    print(f"   Budget: ${profile['budget']:,.0f}")

    # Companies analyzed
    print(f"\n[COMPANIES] Companies Analyzed: {', '.join(results['companies'])}")

    # News analysis
    news = results["news_analysis"]
    print(f"\n[NEWS] News Analysis:")
    print(f"   Articles Analyzed: {news['total_articles']}")
    print(f"   Overall Sentiment: {news['sentiment_summary']}")

    # Rules applied
    rules = results["rules_guidance"]
    print(f"\n[RULES] Investment Rules Applied:")
    for rule in rules["relevant_rules"]:
        print(f"   * {rule}")

    # Stock analysis
    analysis = results["stock_analysis"]
    print(f"\n[ANALYSIS] Stock Analysis Results:")
    for ticker, data in analysis.items():
        print(f"   {ticker}: {data['recommendation']} ({data['confidence']} confidence)")

    # Final recommendations
    recs = results["final_recommendations"]
    print(f"\n[RECOMMENDATIONS] Final Recommendations:")
    if recs["recommendations"]:
        for i, rec in enumerate(recs["recommendations"], 1):
            print(f"   {i}. {rec['ticker']} - {rec['recommendation']} ({rec['confidence']})")
            print(f"      Rationale: {rec['rationale']}")
    else:
        print("   No strong recommendations at this time")

    print(f"\n[DISCLAIMER] {recs['disclaimer']}")

if __name__ == "__main__":
    print("Multi-Agent Stock Analysis System Demo")
    print("=" * 50)
    print("Workflow: Companies -> News -> Stock Analyser -> Suggester")
    print("       Rules RAG -> Stock Analyser")

    workflow = MultiAgentWorkflow()

    # Example 1: Conservative income investor
    result1 = workflow.run_workflow(
        "I'm a conservative investor looking for dividend-paying stocks with $15,000 to invest"
    )
    print_workflow_results(result1)

    # Example 2: Aggressive growth investor
    result2 = workflow.run_workflow(
        "Suggest tech stocks for aggressive growth investors"
    )
    print_workflow_results(result2)

    # Example 3: Moderate balanced investor
    result3 = workflow.run_workflow(
        "What are some balanced investment options for moderate risk tolerance?"
    )
    print_workflow_results(result3)

    print(f"\n{'='*70}")
    print("MULTI-AGENT ARCHITECTURE FEATURES:")
    print("* Companies List Agent: Intelligent company discovery")
    print("* News Agent: Sentiment analysis and news aggregation")
    print("* Rules RAG Agent: Regulatory compliance and investment principles")
    print("* Stock Analyser Agent: Comprehensive financial analysis")
    print("* Suggester Agent: Personalized recommendation synthesis")
    print("* LangGraph Workflow: Coordinated agent execution")
    print("\nArchitecture matches the Excalidraw diagram workflow!")